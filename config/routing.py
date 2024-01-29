from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
     re_path(r'ws/chat/(?P<friendship_id>\d+)/$',
             consumers.DirectMessageConsumer.as_asgi()),
]