from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
     re_path(r'ws/chat/(?P<friendship_id>\d+)/$',consumers.DirectMessageConsumer.as_asgi()),
        re_path(r'ws/room-chat/(?P<room_id>\d+)/$',consumers.RoomMessageConsumer.as_asgi())
]