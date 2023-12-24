from django.db import models
import uuid

from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_details  = models.TextField()
    edited = models.BooleanField(default=False)
    user_post_slug = models.SlugField()


class PostLikes(BaseModel):
    user_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_that_like =  models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.BooleanField(default=False)

class PostComment(BaseModel):
    user_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_that_comment =  models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

class PostCommentLikes(BaseModel):
    user_post_comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    user_that_like =  models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)






