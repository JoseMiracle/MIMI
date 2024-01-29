from django.urls import path
from mimi.chats.api.v1.views import (
    EditOrDeleteMessagesAPIView,
    EditOrDeleteRoomAPIView,
    RoomAPIView,
    UserRoomRequestAPIVIew,
)

app_name = "chats"

urlpatterns = [
    path('edit-or-delete-messages/<uuid:room_name>/', 
         EditOrDeleteMessagesAPIView.as_view(), 
         name='edit_or_delete_messages'),

    
    path('list-or-create-room/', RoomAPIView.as_view(), name='list_or_create_room'),

    path('edit-or-delete-room/<str:room_name>/', 
         EditOrDeleteRoomAPIView.as_view(),
           name='edit_or_delete_room'),

    
    path('user-room-request/', UserRoomRequestAPIVIew.as_view(), name='user_room_request')

]