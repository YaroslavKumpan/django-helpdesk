
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    """
    Валидирует токен и возвращает пользователя или AnonymousUser.
    """
    try:
        access_token = AccessToken(token)  # проверяет подпись и срок
        user = User.objects.get(id=access_token['user_id'])
        return user
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    ASGI middleware для аутентификации по JWT токену в query-параметре.
    Токен ожидается в виде ?token=... в URL WebSocket.
    """
    async def __call__(self, scope, receive, send):
        # Получаем query_string из scope (это байты, декодируем)
        query_string = scope.get('query_string', b'').decode()
        # Разбираем параметры запроса
        query_params = parse_qs(query_string)
        # Берём первый (и единственный) токен из параметра 'token'
        token = query_params.get('token', [None])[0]

        if token:
            # Асинхронно получаем пользователя по токену
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        # Передаём управление дальше (к роутеру и consumer'у)
        return await super().__call__(scope, receive, send)