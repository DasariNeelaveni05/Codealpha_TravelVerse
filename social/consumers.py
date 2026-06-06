import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        user = self.scope['user']

        if message_text and user.is_authenticated:
            # Save message to DB
            msg_obj = await self.save_message(user, self.room_name, message_text)
            
            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'user': user.username,
                    'avatar': user.profile.get_avatar(),
                    'created': msg_obj.created_at.strftime('%I:%M %p')
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user, room_slug, text):
        room = ChatRoom.objects.get(slug=room_slug)
        # Ensure user is a member
        if user not in room.members.all():
            room.members.add(user)
        return ChatMessage.objects.create(
            room=room,
            user=user,
            text=text
        )