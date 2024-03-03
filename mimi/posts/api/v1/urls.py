from django.urls import path
from mimi.posts.api.v1.views import (
    CreatePostAPIView,
    UpdatePostAPIView,
    UserPostAPIView,
    MakeReactionToPostAPIView,
    RemoveReactionFromPostAPIView,
    CommentToPostAPIView,
    ReplyToCommentAPIView,
    RepliesToCommentAPIView,
)

app_name = "posts"


urlpatterns = [
    path('create-post/', CreatePostAPIView.as_view(), name='create-post'),
    path('update-post/<uuid:post_id>/', UpdatePostAPIView.as_view(), name='update_post'),
    path('post-by/<str:username>/<uuid:post_id>/', UserPostAPIView.as_view(), name='user_post'),
    path('make-reaction-to-post/', MakeReactionToPostAPIView.as_view(), name='make-reaction-to-post'),
    path('remove-reaction-from-post/<uuid:post_reaction_id>/', RemoveReactionFromPostAPIView.as_view(), name='remove-reaction-from-post/<post_reaction_id>/'),
    path('comment/', CommentToPostAPIView.as_view(), name='comment'),
    path('comments-to-post/<uuid:post_id>/', CommentToPostAPIView.as_view(), name='comments-to-post'),
    path('reply-to-comment/', ReplyToCommentAPIView.as_view(), name='reply_to_comment'),
    path('replies-to-comment/<uuid:parent_comment_id>/', RepliesToCommentAPIView.as_view(), name='replies_to_comment')
]