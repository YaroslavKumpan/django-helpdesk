import json
from datetime import timezone

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import SupportRequest, SupportMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Вызывается при подключении клиента
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Проверка авторизации (позже)
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            # Проверка прав (пользователь может подключаться только к своей заявке или support)
            can_join = await self.check_permission(user, self.room_id)
            if not can_join:
                await self.close()
            else:
                # Добавляем пользователя в группу (комнату)
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу при отключении
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Получение сообщения от клиента
        data = json.loads(text_data)
        message = data.get('message')

        user = self.scope['user']
        # Сохраняем сообщение в БД
        await self.save_message(user, self.room_id, message)

        # Отправляем сообщение всем в группе
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.username,
                'timestamp': str(timezone.now())  # добавим импорт
            }
        )

    async def chat_message(self, event):
        # Отправка сообщения клиенту (вызывается group_send)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def check_permission(self, user, room_id):
        try:
            support_request = SupportRequest.objects.get(id=room_id)
        except SupportRequest.DoesNotExist:
            return False
        # Разрешаем, если пользователь автор, поддержка или админ
        if user.profile.role in ['support', 'admin']:
            return True
        return support_request.user == user.profile

    @database_sync_to_async
    def save_message(self, user, room_id, text):
        support_request = SupportRequest.objects.get(id=room_id)
        SupportMessage.objects.create(
            sender=user,
            support_request=support_request,
            text=text
        )