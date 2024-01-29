from rest_framework import generics,viewsets, permissions
from mimi.chats.models import Message
from mimi.chats.api.v1.serializers import (
    EditOrDeleteMessageSerializer,
    RoomSerializer,
    JoinRoomRequestSerializer
)
from mimi.chats.utils.constants import (
    PENDING_ROOM_REQUEST,
    ACCEPTED_ROOM_REQUEST
)
from mimi.chats.api.v1.permissions import IsRoomAdmin
from mimi.chats.models import (
    Room,
    JoinRoomRequests
)



class EditOrDeleteMessagesAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EditOrDeleteMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Message.objects.all()

    
    def get_object(self):
        message_obj = Message.objects.get(id=self.kwargs['message_id'])
        return message_obj

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    


class RoomAPIView(generics.ListCreateAPIView):

    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsRoomAdmin]

    def get_queryset(self):
        room_queryset = Room.objects.all().filter(is_public=True)
        return room_queryset
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
class EditOrDeleteRoomAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsRoomAdmin]
    serializer_class = RoomSerializer

    def get_object(self):
        room_obj = Room.objects.filter(room_name=self.kwargs['room_name']).first()    
        return room_obj
    
    def put(self, request, *args, **kwargs):
        self.check_object_permissions(self.request, self.get_object())
        return super().put(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
        

# USERS
    
class UserRoomRequestAPIVIew(generics.ListCreateAPIView):
    serializer_class = JoinRoomRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    
    def get_queryset(self):
        join_room_request_queryset = JoinRoomRequests.objects.all().filter(
            user=self.request.user,
            room_request=PENDING_ROOM_REQUEST
        )
        return join_room_request_queryset
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


