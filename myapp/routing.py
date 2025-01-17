from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/reading_room/<int:room_id>/', consumers.ReadingRoomConsumer.as_asgi()),
]