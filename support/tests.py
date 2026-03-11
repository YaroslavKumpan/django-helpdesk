import asyncio

import pytest
from asgiref.sync import sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.urls import re_path
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from .consumers import ChatConsumer
from .middleware import JWTAuthMiddleware
from .models import SupportRequest, SupportMessage


# ========== Фикстуры ==========

@pytest.fixture
def api_client():
    """Возвращает простой APIClient."""
    return APIClient()

@pytest.fixture
def test_user(db):
    """Создаёт обычного пользователя для тестов."""
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def support_user(db):
    """Создаёт пользователя с ролью support."""
    user = User.objects.create_user(username='support', password='12345')
    user.profile.role = 'support'
    user.profile.save()
    return user

@pytest.fixture
def admin_user(db):
    """Создаёт администратора."""
    user = User.objects.create_user(username='admin', password='12345', is_staff=True)
    user.profile.role = 'admin'
    user.profile.save()
    return user

@pytest.fixture
def auth_client(api_client, test_user):
    """Возвращает APIClient с авторизацией по JWT (обычный пользователь)."""
    login_response = api_client.post('/api/login/', {'username': 'testuser', 'password': '12345'})
    token = login_response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

@pytest.fixture
def support_client(api_client, support_user):
    """APIClient для пользователя с ролью support."""
    login_response = api_client.post('/api/login/', {'username': 'support', 'password': '12345'})
    token = login_response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

@pytest.fixture
def test_request(test_user):
    """Создаёт тестовую заявку."""
    return SupportRequest.objects.create(
        user=test_user.profile,
        title='Test Request',
        description='Test Description'
    )

# ========== Тесты моделей ==========

@pytest.mark.django_db
def test_user_profile_created_on_user_creation():
    """При создании пользователя должен автоматически создаваться профиль."""
    user = User.objects.create_user(username='testuser2', password='12345')
    assert hasattr(user, 'profile')
    assert user.profile.role == 'user'
    assert user.profile.is_support is False

@pytest.mark.django_db
def test_support_request_creation(test_user):
    """Проверка создания заявки."""
    request = SupportRequest.objects.create(
        user=test_user.profile,
        title='Title',
        description='Description'
    )
    assert request.status == 'new'
    assert request.user == test_user.profile
    assert str(request) == 'Title (New)'


@pytest.mark.django_db
def test_is_support_property(test_user):
    """Проверка свойства is_support у профиля."""
    profile = test_user.profile
    assert profile.is_support is False

    profile.role = 'support'
    profile.save()
    profile.refresh_from_db()
    assert profile.is_support is True

@pytest.mark.django_db
def test_support_message_creation(test_request, test_user):
    """Проверка создания сообщения."""
    message = SupportMessage.objects.create(
        sender=test_user,
        support_request=test_request,
        text='Hello'
    )
    assert message.text == 'Hello'
    assert message.read is False
    assert message.sender == test_user
    assert message.support_request == test_request

# ========== Тесты API ==========

@pytest.mark.django_db
def test_user_registration_success(api_client):
    """Успешная регистрация пользователя."""
    data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'StrongPass123',
        'password2': 'StrongPass123'
    }
    response = api_client.post('/api/register/', data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username='newuser').exists()

@pytest.mark.django_db
def test_user_registration_password_mismatch(api_client):
    """Регистрация с несовпадающими паролями."""
    data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'StrongPass123',
        'password2': 'WrongPass'
    }
    response = api_client.post('/api/register/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password2' in response.data

@pytest.mark.django_db
def test_user_login_success(api_client, test_user):
    """Успешный логин."""
    data = {'username': 'testuser', 'password': '12345'}
    response = api_client.post('/api/login/', data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

@pytest.mark.django_db
def test_user_login_invalid_credentials(api_client):
    """Логин с неверными данными."""
    data = {'username': 'wrong', 'password': 'wrong'}
    response = api_client.post('/api/login/', data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_create_support_request_authenticated(auth_client, test_user):
    """Создание заявки авторизованным пользователем."""
    data = {'title': 'New Request', 'description': 'Help'}
    response = auth_client.post('/api/requests/', data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == 'New Request'
    assert response.data['user']['username'] == test_user.username
    assert SupportRequest.objects.filter(user=test_user.profile).exists()

@pytest.mark.django_db
def test_create_support_request_unauthenticated(api_client):
    """Попытка создать заявку без аутентификации."""
    data = {'title': 'New Request', 'description': 'Help'}
    response = api_client.post('/api/requests/', data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_create_request_without_title_fails(auth_client):
    """Создание заявки без заголовка (проверка валидации сериализатора)."""
    data = {'description': 'Test description'}
    response = auth_client.post('/api/requests/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'title' in response.data

@pytest.mark.django_db
def test_list_requests_user_sees_only_own(auth_client, test_user, test_request):
    """Обычный пользователь видит только свои заявки."""
    # Создадим другую заявку от другого пользователя
    other_user = User.objects.create_user(username='other', password='12345')
    SupportRequest.objects.create(user=other_user.profile, title='Other', description='Other')
    response = auth_client.get('/api/requests/')
    assert response.status_code == status.HTTP_200_OK
    # Должна быть только одна заявка (тестовая)
    assert len(response.data) == 1
    assert response.data[0]['title'] == 'Test Request'

@pytest.mark.django_db
def test_support_sees_all_requests(support_client, test_request):
    """Поддержка видит все заявки."""
    other_user = User.objects.create_user(username='other', password='12345')
    SupportRequest.objects.create(user=other_user.profile, title='Other', description='Other')
    response = support_client.get('/api/requests/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

@pytest.mark.django_db
def test_update_request_status_as_user(auth_client, test_request):
    """Обычный пользователь не может менять статус заявки."""
    data = {'status': 'in_progress'}
    response = auth_client.patch(f'/api/requests/{test_request.id}/', data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_update_request_status_as_support(support_client, test_request):
    """Поддержка может менять статус."""
    data = {'status': 'in_progress'}
    response = support_client.patch(f'/api/requests/{test_request.id}/', data, format='json')
    assert response.status_code == status.HTTP_200_OK
    test_request.refresh_from_db()
    assert test_request.status == 'in_progress'

@pytest.mark.django_db
def test_delete_request_as_user(auth_client, test_request):
    """Обычный пользователь не может удалить заявку."""
    response = auth_client.delete(f'/api/requests/{test_request.id}/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_delete_request_as_admin(admin_user, api_client, test_request):
    """Администратор может удалить заявку."""
    # Логинимся как админ
    login_response = api_client.post('/api/login/', {'username': 'admin', 'password': '12345'})
    token = login_response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.delete(f'/api/requests/{test_request.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not SupportRequest.objects.filter(id=test_request.id).exists()

@pytest.mark.django_db
def test_get_message_history(auth_client, test_request, test_user):
    """Получение истории сообщений заявки."""
    SupportMessage.objects.create(sender=test_user, support_request=test_request, text='First')
    SupportMessage.objects.create(sender=test_user, support_request=test_request, text='Second')
    response = auth_client.get(f'/api/requests/{test_request.id}/messages/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    # В action сортируем по убыванию created_at, поэтому сначала новые
    assert response.data[0]['text'] == 'Second'

# ========== Тесты WebSocket ==========

@pytest.fixture
def ws_application():
    """Возвращает приложение WebSocket с роутером и JWT middleware."""
    application = URLRouter([
        re_path(r'ws/chat/(?P<room_id>\d+)/$', ChatConsumer.as_asgi()),
    ])
    # Оборачиваем в JWTAuthMiddleware для обработки токена из query-параметра
    return JWTAuthMiddleware(application)

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_connect_with_valid_token(ws_application, test_request, test_user):
    """Подключение к WebSocket с валидным токеном."""
    token = str(AccessToken.for_user(test_user))
    url = f'/ws/chat/{test_request.id}/?token={token}'
    communicator = WebsocketCommunicator(ws_application, url)
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_connect_with_invalid_token(ws_application, test_request):
    """Подключение с неверным токеном должно быть отклонено."""
    url = f'/ws/chat/{test_request.id}/?token=invalid'
    communicator = WebsocketCommunicator(ws_application, url)
    connected, _ = await communicator.connect()
    assert not connected

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_connect_without_token(ws_application, test_request):
    """Подключение без токена должно быть отклонено."""
    url = f'/ws/chat/{test_request.id}/'
    communicator = WebsocketCommunicator(ws_application, url)
    connected, _ = await communicator.connect()
    assert not connected

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_send_message_via_websocket(ws_application, test_request, test_user):
    token = str(AccessToken.for_user(test_user))
    url = f'/ws/chat/{test_request.id}/?token={token}'
    communicator = WebsocketCommunicator(ws_application, url)
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to({'message': 'Hello via WS'})
    await asyncio.sleep(0.1)

    exists = await sync_to_async(
        SupportMessage.objects.filter(
            support_request=test_request, text='Hello via WS'
        ).exists
    )()
    assert exists

    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_typing_indicator(ws_application, test_request, test_user):
    token = str(AccessToken.for_user(test_user))
    url = f'/ws/chat/{test_request.id}/?token={token}'
    communicator = WebsocketCommunicator(ws_application, url)
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to({'type': 'typing', 'status': 'start'})
    with pytest.raises(asyncio.TimeoutError):
        await communicator.receive_json_from(timeout=0.1)

    # Даем время на обработку и игнорируем возможные ошибки при закрытии
    await asyncio.sleep(0.1)
    try:
        await communicator.disconnect()
    except asyncio.CancelledError:
        pass