from django.db import models
from django.contrib.auth import get_user_model
from mimi.utils.base_class import BaseModel
from mimi.chats.utils.constants import (
    PENDING_ROOM_REQUEST,
    ACCEPTED_ROOM_REQUEST
)
User = get_user_model()




class Message(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, related_name="sender_mesages", null=True )
    receiver = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, related_name="receiver_messages", null=True)
    edit_count = models.IntegerField(default=0)
    message = models.TextField()

    def __str__(self):
        return self.message



class Room(BaseModel):
    room_creator_id = models.CharField(max_length=250, blank=False, null=False)
    room_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    number_of_persons = models.IntegerField(default=100)
    is_public = models.BooleanField(default=True)
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)


class JoinRoomRequests(BaseModel):

    ROOM_REQUEST_CHOICES = [
        (PENDING_ROOM_REQUEST, 'PENDING'),
        (ACCEPTED_ROOM_REQUEST, 'ACCEPTED'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="rooms")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_room_request")
    room_request = models.CharField(max_length=20, default=ROOM_REQUEST_CHOICES[0][0], choices=ROOM_REQUEST_CHOICES)


class RoomMembers(BaseModel):
    is_admin = models.BooleanField(default=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    room_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_room_member")


class RoomMessages(BaseModel):    
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    message = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    is_locked = models.BooleanField(default=False)
    

