from factory.django import DjangoModelFactory
from mimi.chats.models import Room, RoomMembers, JoinRoomRequests
from tests.accounts.factories import UserFactory
import pytest


class RoomFactory(DjangoModelFactory):
    class Meta:
        model = Room
    
    
    room_name = 'UNIQUE ROOM'
    is_public = True
    description = "I love this group"


class RoomMembersFactory(DjangoModelFactory):
    
    class Meta:
        model  = RoomMembers
    is_admin = False


class JoinRoomRequestsFactory(DjangoModelFactory):
    class Meta:
        model = JoinRoomRequests

    room_request = 'PENDING'

