from rest_framework import generics, permissions, status
from mimi.friendships.api.v1.serializers import (
    SendFriendRequestSerializer,
    UserSentFriendRequestSerializer,
    ReceivedFriendRequestSerializer,
    AcceptFriendRequestSerializer,
    UserFriendsSerializer,
)

# from mimi.accounts.models import UsersBlockedByUser
from rest_framework.response import Response

from mimi.friendships.models import (
    FriendRequest,
    Friends,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class SendFriendRequestAPIView(generics.CreateAPIView):
    serializer_class = SendFriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user_pending_sent_friend_requests = FriendRequest.objects.filter(
            sender=self.request.user, status="pending"
        )

        return user_pending_sent_friend_requests

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserSentFriendRequestAPIView(generics.ListAPIView):
    serializer_class = UserSentFriendRequestSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user_pending_sent_friend_requests = FriendRequest.objects.filter(
            sender=self.request.user, status="pending"
        )

        return user_pending_sent_friend_requests


class ReceivedFriendRequestAPIView(generics.ListAPIView):
    serializer_class = ReceivedFriendRequestSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user_pending_received_friend_requests = FriendRequest.objects.filter(
            receiver=self.request.user, status="pending"
        )

        return user_pending_received_friend_requests


class UserCancelOrRejectFriendRequestAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        friendship_obj = FriendRequest.objects.filter(
            id=self.kwargs["friend_request_id"], sender=self.request.user
        ).first()

        return friendship_obj

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if instance is None:
            return Response(data={"status": "error"}, status=status.HTTP_204_NO_CONTENT)
        return super().perform_destroy(instance)


class AcceptFriendRequestAPIView(generics.UpdateAPIView):
    serializer_class = AcceptFriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        friend_request_obj = FriendRequest.objects.filter(
            id=self.kwargs["friend_request_id"]
        ).first()

        return friend_request_obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = self.request.data["status"]
        instance.save()
        try:
            Friends.objects.create(user=self.request.user, friend=instance.sender)
            return Response(
                {"message": "friendship accepted"}, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {"message": "friendship accepted already"}, status=status.HTTP_200_OK
            )


class UserFriendsAPIView(generics.ListAPIView):
    serializer_class = UserFriendsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = User.objects.get(username=self.request.user.username)
        blocked_user_ids = UsersBlockedByUser.objects.filter(user=user).values_list(
            "other_user_id", flat=True
        )
        user_friends_queryset = Friends.objects.filter(user=user).exclude(
            friend_id__in=blocked_user_ids
        )

        return user_friends_queryset
