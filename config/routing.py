from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    
     re_path(r'ws/chat/(?P<chat_id>[0-9a-fA-F-]{36})/$', consumers.DirectMessageConsumer.as_asgi()),
     re_path(r'ws/room-chat/(?P<room_id>\d+)/$',consumers.RoomMessageConsumer.as_asgi()), 
     re_path(r'ws/chat/(?P<chat_name>[0-9a-zA-Z-_.@]+)/$', consumers.ChatConsumer.as_asgi()),

]