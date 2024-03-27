from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from mimi.chats.models import Message
from mimi.chats.api.v1.serializers import (
    EditOrDeleteMessageSerializer,
    RoomSerializer,
    JoinRoomRequestSerializer,
    AcceptOrRejectUserRoomRequestSerializer,
    GetAllUsersInTheRoomSerializer,
    MessageSerializer,
)
from mimi.chats.utils.constants import (
    PENDING_ROOM_REQUEST,
    ACCEPTED_ROOM_REQUEST,
    REJECT_ROOM_REQUEST,
)
from mimi.chats.api.v1.permissions import IsRoomAdmin
from mimi.chats.models import (
    Room,
    JoinRoomRequests,
    RoomMembers,
)

from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()


class EditOrDeleteMessagesAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EditOrDeleteMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Message.objects.all()

    def get_object(self):
        message_obj = Message.objects.get(id=self.kwargs["message_id"])
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
        room_obj = Room.objects.filter(room_name=self.kwargs["room_name"]).first()
        return room_obj

    def put(self, request, *args, **kwargs):
        self.check_object_permissions(self.request, self.get_object())
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class AcceptOrRejectUserRoomRequestAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsRoomAdmin]
    serializer_class = AcceptOrRejectUserRoomRequestSerializer

    def get_object(self):
        user_room_request_obj = JoinRoomRequests.objects.filter(
            id=self.kwargs["user_room_request_id"]
        ).first()
        return user_room_request_obj

    def put(self, request, *args, **kwargs):
        self.check_object_permissions(self.request, self.get_object())
        return super().put(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user = self.get_object().user
        user_room_request_obj = self.get_object()
        if request.data["decision"] == REJECT_ROOM_REQUEST:
            user_room_request_obj.delete()
            return Response({"messsage": "room request rejected"})
        user_room_request_obj.room_request = ACCEPTED_ROOM_REQUEST
        user_room_request_obj.save()

        # Adding the user to the room

        room = Room.objects.filter(room_name=self.kwargs["room_name"]).first()
        room_member = RoomMembers.objects.create(
            is_admin=False, room=room, room_member=user
        )

        return Response({"message": "user room request accepted."})


class UserRoomRequestAPIVIew(generics.ListCreateAPIView):
    serializer_class = JoinRoomRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        join_room_request_queryset = JoinRoomRequests.objects.all().filter(
            user=self.request.user, room_request=PENDING_ROOM_REQUEST
        )
        return join_room_request_queryset

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserRoomsAPIView(generics.ListAPIView):
    serializer_class = JoinRoomRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_accepted_rooms_queryset = JoinRoomRequests.objects.filter(
            user=self.request.user, room_request=ACCEPTED_ROOM_REQUEST
        )
        return user_accepted_rooms_queryset

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GetAllUsersInTheRoomAPIView(generics.ListAPIView):
    serializer_class = GetAllUsersInTheRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room = Room.objects.filter(room_name=self.kwargs["room_name"]).first()
        user_in_room = RoomMembers.objects.filter(
            room=room, room_member=self.request.user
        ).first()

        if user_in_room:
            room_member_queryset = RoomMembers.objects.filter(room=room)
            return room_member_queryset
        else:
            return None

    def get(self, request, *args, **kwargs):
        if self.get_queryset() == None:
            return Response(
                {"error": f"you don't belong to {self.kwargs['room_name']}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().get(request, *args, **kwargs)


class RemoveUserFromARoomAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsRoomAdmin]

    def get_object(self):
        room = Room.objects.filter(room_name=self.kwargs["room_name"]).first()
        user = User.objects.filter(username=self.kwargs["username"]).first()

        room_member_obj = RoomMembers.objects.filter(
            room=room, room_member=user
        ).first()
        if room and user and room_member_obj:
            return room_member_obj
        return None

    def post(self, request, *args, **kwargs):
        self.check_object_permissions(self.request, self.get_object())
        room_member_obj = self.get_object()

        if room_member_obj is not None:
            joined_room_request_obj = JoinRoomRequests.objects.filter(
                room=room_member_obj.room, user=room_member_obj.room_member
            ).first()
            joined_room_request_obj.delete()
            room_member_obj.delete()
            return Response(
                {"message": f"{room_member_obj.room_member.username} removed from room"}
            )

        return Response(
            {"errror": "room doesn't exist or unknown user"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserLeaveRoomAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        room = Room.objects.filter(room_name=self.kwargs["room_name"]).first()
        room_member_obj = RoomMembers.objects.filter(
            room=room, room_member=self.request.user
        ).first()

        if room and room_member_obj:
            return room_member_obj
        return None

    def post(self, request, *args, **kwargs):
        room_member_obj = self.get_object()

        if room_member_obj is not None:
            joined_room_request_obj = JoinRoomRequests.objects.filter(
                room=room_member_obj.room, user=room_member_obj.room_member
            ).first()
            joined_room_request_obj.delete()
            room_member_obj.delete()
            return Response(
                {"message": f"{room_member_obj.room_member.username} removed from room"}
            )

        return Response(
            {"errror": "room doesn't exist or unknown user"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class MessageAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        condition_1 = Q(receiver=self.kwargs["other_user_id"], sender=self.request.user)
        condition_2 = Q(sender=self.kwargs["other_user_id"], receiver=self.request.user)
        message_queryset = Message.objects.filter(condition_1 | condition_2).all()

        return message_queryset

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
