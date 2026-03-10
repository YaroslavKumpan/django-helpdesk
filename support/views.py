from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Логин: принимает username и password, возвращает access token (в теле)
    и устанавливает refresh token в httpOnly cookie.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Получаем refresh token из ответа (он есть в data.refresh)
            refresh_token = response.data.get('refresh')
            # Устанавливаем cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT.get('AUTH_COOKIE'),
                value=refresh_token,
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                httponly=settings.SIMPLE_JWT.get('AUTH_COOKIE_HTTP_ONLY', True),
                samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
                path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/'),
            )
            # Удаляем refresh из тела ответа, чтобы клиент его не видел
            del response.data['refresh']
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Обновление access token: ожидает, что refresh token будет в cookie.
    Возвращает новый access token (в теле) и, если включено ROTATE_REFRESH_TOKENS,
    обновляет refresh token в cookie.
    """
    def post(self, request, *args, **kwargs):
        # Достаём refresh token из cookie
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT.get('AUTH_COOKIE'))
        if not refresh_token:
            return Response({'detail': 'Refresh token not found'}, status=400)

        # Передаём его в сериализатор (как будто пришёл в теле)
        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        serializer.is_valid(raise_exception=True)

        # Получаем данные (новый access и, если rotate, новый refresh)
        response = Response(serializer.validated_data, status=200)

        # Если есть новый refresh token, обновляем cookie
        if 'refresh' in serializer.validated_data:
            response.set_cookie(
                key=settings.SIMPLE_JWT.get('AUTH_COOKIE'),
                value=serializer.validated_data['refresh'],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                httponly=settings.SIMPLE_JWT.get('AUTH_COOKIE_HTTP_ONLY', True),
                samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
                path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/'),
            )
            # Удаляем refresh из тела, чтобы клиент не получил его
            del response.data['refresh']

        return response