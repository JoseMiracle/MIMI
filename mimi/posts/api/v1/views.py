from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from mimi.posts.models import PostReaction
from mimi.posts.api.v1.serializers import (
    PostSerializer,
    UpdatePostSerializer,
    ReactionToPostSerializer,
    CommentToPostSerializer,
    ReplyToCommentSerializer,
    RepliesToCommentSerializer,
)
from mimi.posts.models import Post, CommentToPost
from mimi.posts.api.v1.permissions import IsUserBlocked

User = get_user_model()


class CreatePostAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UpdatePostAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdatePostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        post_obj = Post.objects.filter(
            id=self.kwargs["post_id"], user=self.request.user
        ).first()
        return None if post_obj is None else post_obj

    def get(self, request, *args, **kwargs):
        if self.get_object() is None:
            return self.obj_is_none_response()
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if self.get_object() is None:
            return self.obj_is_none_response()
        return super().put(request, *args, **kwargs)

    def obj_is_none_response(self):
        return Response(
            {"status": "false", "message": "post doesn't exist"},
            status=status.HTTP_200_OK,
        )


class UserPostAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsUserBlocked]
    serializer_class = PostSerializer

    def get_object(self):
        user = User.objects.get(username=self.kwargs["username"])
        user_post_obj = Post.objects.filter(
            user=user, id=self.kwargs["post_id"]
        ).first()
        return user_post_obj

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MakeReactionToPostAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReactionToPostSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RemoveReactionFromPostAPIView(generics.RetrieveDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReactionToPostSerializer

    def get_object(self):
        post_reaction_obj = PostReaction.objects.filter(
            user_that_react=self.request.user, id=self.kwargs["post_reaction_id"]
        ).first()
        return post_reaction_obj

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CommentToPostAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentToPostSerializer

    def get_queryset(self):
        post = Post.objects.filter(id=self.kwargs["post_id"]).first()
        comments_to_post_objs = CommentToPost.objects.filter(
            post=post, parent_comment=None
        )
        print(comments_to_post_objs.count())
        return comments_to_post_objs

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CommentToPostReactionAPIVIew(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    #  serializer_class =

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ReplyToCommentAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReplyToCommentSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


generics.RetrieveAPIView


class RepliesToCommentAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RepliesToCommentSerializer

    def get_queryset(self):
        parent_comment_id = self.kwargs["parent_comment_id"]
        nested_replies = CommentToPost.objects.filter(
            parent_comment_id=parent_comment_id
        ).select_related("user_that_comment")
        return nested_replies
