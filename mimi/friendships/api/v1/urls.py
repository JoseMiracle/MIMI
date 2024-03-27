from django.urls import path
from mimi.friendships.api.v1.views import (
    SendFriendRequestAPIView,
    UserSentFriendRequestAPIView,
    ReceivedFriendRequestAPIView,
    UserCancelOrRejectFriendRequestAPIView,
    AcceptFriendRequestAPIView,
    UserFriendsAPIView,
)

app_name = "friendships"

urlpatterns = [
    path(
        "send-friend-request/",
        SendFriendRequestAPIView.as_view(),
        name="send_friend_request",
    ),
    path(
        "user-sent-friend-requests/",
        UserSentFriendRequestAPIView.as_view(),
        name="user-sent-friend-requests",
    ),
    path(
        "user-received-friend-requests/",
        ReceivedFriendRequestAPIView.as_view(),
        name="user-received-friend-requests",
    ),
    path(
        "user-cancel-or-reject-friend-request/<uuid:friend_request_id>",
        UserCancelOrRejectFriendRequestAPIView.as_view(),
        name="user-cancel-or-reject-friend-request",
    ),
    path(
        "accept-friend-request/<uuid:friend_request_id>/",
        AcceptFriendRequestAPIView.as_view(),
        name="accept-friend-request",
    ),
    path("user-friends/", UserFriendsAPIView.as_view(), name="user_friends"),
]
