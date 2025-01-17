import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ReadingRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'reading_room_{self.room_id}'

        # Присоединяемся к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']

        if message_type == 'progress_update':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'progress_update',
                    'user': data['user'],
                    'current_page': data['current_page']
                }
            )
        elif message_type == 'chat_message':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'user': data['user'],
                    'message': data['message']
                }
            )

    async def progress_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'user': event['user'],
            'current_page': event['current_page']
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'user': event['user'],
            'message': event['message']
        }))