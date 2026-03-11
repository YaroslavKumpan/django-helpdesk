import pytest
from django.contrib.auth.models import User
from .models import UserProfile, SupportRequest, SupportMessage

# ========== Тесты моделей ==========

@pytest.mark.django_db
def test_user_profile_created_on_user_creation():
    """
    При создании пользователя должен автоматически создаваться профиль
    с ролью 'user'.
    """
    user = User.objects.create_user(username='testuser', password='12345')
    # Проверяем, что профиль существует и имеет правильную роль
    assert hasattr(user, 'profile')
    assert user.profile.role == 'user'
    assert user.profile.is_support is False

@pytest.mark.django_db
def test_support_request_creation():
    user = User.objects.create_user(username='testuser', password='12345')
    request = SupportRequest.objects.create(
        user=user.profile,
        title='Test Request',
        description='Test Description'
    )
    assert request.status == 'new'
    assert request.user == user.profile
    assert str(request) == 'Test Request (New)'
    assert request.created_at is not None
    assert request.updated_at is None  # только что созданная заявка не имеет даты обновления

@pytest.mark.django_db
def test_is_support_property():
    user = User.objects.create_user(username='testuser')
    profile = user.profile
    assert profile.is_support is False

    profile.role = 'support'
    profile.save()
    # Обновляем объект из БД, чтобы убедиться, что изменения применились
    profile.refresh_from_db()
    assert profile.is_support is True

@pytest.mark.django_db
def test_support_request_title_required():
    user = User.objects.create_user(username='testuser')
    with pytest.raises(Exception):  # Ожидаем исключение при попытке создать без title
        SupportRequest.objects.create(user=user.profile, description='No title')
