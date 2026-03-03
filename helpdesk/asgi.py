import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from support import routing  # создадим позже

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),  # обычные HTTP запросы
    'websocket': AuthMiddlewareStack(  # WebSocket с поддержкой авторизации
        URLRouter(
            routing.websocket_urlpatterns  # наши маршруты WebSocket
        )
    ),
})