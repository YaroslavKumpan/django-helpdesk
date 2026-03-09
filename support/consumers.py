import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # logger.info(f"Попытка подключения к комнате {self.room_id}, пользователь {self.scope['user']}")

        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            can_join = await self.check_permission(user, self.room_id)
            if not can_join:
                await self.close()
            else:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type", "message")  # по умолчанию тип 'message'

        if message_type == "message":
            # Обычное текстовое сообщение
            message = data.get("message")
            user = self.scope["user"]
            await self.save_message(user, self.room_id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "user": user.username,
                    "timestamp": str(timezone.now()),
                    "sender_channel": self.channel_name,
                },
            )
        elif message_type == "typing":
            # Событие печати
            status = data.get("status")  # 'start' или 'stop'
            user = self.scope["user"]
            # Отправляем событие всем в группе, но исключая отправителя
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_notification",
                    "user": user.username,
                    "status": status,
                    "sender_channel": self.channel_name,  # идентификатор отправителя
                },
            )

    async def typing_notification(self, event):
        # Этот метод вызывается, когда мы делаем group_send с type='typing_notification'
        # Проверяем, не отправитель ли это
        if event["sender_channel"] != self.channel_name:
            await self.send(
                text_data=json.dumps(
                    {"type": "typing", "user": event["user"], "status": event["status"]}
                )
            )

    async def chat_message(self, event):
        if event["sender_channel"] != self.channel_name:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": event["message"],
                        "user": event["user"],
                        "timestamp": event["timestamp"],
                    }
                )
            )

    @database_sync_to_async
    def check_permission(self, user, room_id):
        from .models import SupportRequest
        try:
            support_request = SupportRequest.objects.get(id=room_id)
        except SupportRequest.DoesNotExist:
            return False
        if user.profile.role in ['support', 'admin']:
            return True
        return support_request.user == user.profile

    @database_sync_to_async
    def save_message(self, user, room_id, text):
        from .models import SupportRequest, SupportMessage
        support_request = SupportRequest.objects.get(id=room_id)
        SupportMessage.objects.create(
            sender=user,
            support_request=support_request,
            text=text
        )
