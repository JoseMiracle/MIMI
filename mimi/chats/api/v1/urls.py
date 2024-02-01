from django.urls import path
from mimi.chats.api.v1.views import (
    EditOrDeleteMessagesAPIView,
    EditOrDeleteRoomAPIView,
    RoomAPIView,
    UserRoomRequestAPIVIew,
    AcceptOrRejectUserRoomRequestAPIView,
    UserRoomsAPIView,
    GetAllUsersInTheRoomAPIView,
    RemoveUserFromARoomAPIView,

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
    
    path('user-room-request/', 
         UserRoomRequestAPIVIew.as_view(), 
         name='user_room_request'),
        
    path('accept_or_reject_room_request/<str:room_name>/<uuid:user_room_request_id>/', 
         AcceptOrRejectUserRoomRequestAPIView.as_view(), 
         name='accept_or_reject_room_request'),

    path('user-rooms/', UserRoomsAPIView.as_view(), name='user_rooms'),
    path('get-user-in-room/<str:room_name>/',
          GetAllUsersInTheRoomAPIView.as_view(), 
          name='get_user_in_room'),

    path('remove-user-from-room/<str:room_name>/<str:username>/', RemoveUserFromARoomAPIView.as_view(), name='remove_user_from_room')

]