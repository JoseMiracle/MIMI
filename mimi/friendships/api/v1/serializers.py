from typing import Any
from rest_framework import serializers
from mimi.friendships.models import FriendRequest, Friends
from django.contrib.auth import get_user_model
from mimi.accounts.api.v1.serializers import UserSerializer

User = get_user_model()


class SendFriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ["sender", "receiver", "status"]

    def validate(self, attrs: dict) -> dict[str | Any]:
        friend_request_obj = FriendRequest.objects.filter(
            sender=self.context["request"].user,
            receiver=attrs["receiver"],
            status="pending",
        )

        if self.context["request"].user == attrs["receiver"]:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "error-message": "you can't send friend request to yourself",
                }
            )

        elif friend_request_obj.exists():
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "error-message": "friend request send already(pending)",
                }
            )

        return attrs

    def create(self, validated_data):
        FriendRequest.objects.create(
            sender=self.context["request"].user,
            receiver=validated_data["receiver"],
            status=validated_data["status"],
        )

        return validated_data


class UserSentFriendRequestSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ["id", "receiver"]


class ReceivedFriendRequestSerializer(serializers.ModelSerializer):
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ["id", "receiver"]


class AcceptFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ["status"]


class UserFriendsSerializer(serializers.ModelSerializer):
    friend = UserSerializer()

    class Meta:
        model = Friends
        fields = ["user", "friend"]
