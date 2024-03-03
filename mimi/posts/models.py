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

def post_images_upload_location(instance,filename):
    return f"posts/images/{filename}" 


def comment_images_upload_location(instance, filename: str) -> str:
    """Get Location for user profile photo upload."""
    return f"comment/images/{filename}"

class Post(BaseModel):
    POST_CHOICES = [
        ('draft', 'draft'),
        ('published', 'published')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_details  = models.TextField()
    edited = models.BooleanField(default=False)
    post_state = models.CharField(max_length=11, choices=POST_CHOICES, default='draft')

    
    def __str__(self):
        return f"{self.post_details}{self.post_state}" 
    

class PostImage(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    post_image = models.ImageField(upload_to=post_images_upload_location, blank=True)
    
    def __str__(self):
        return f"{self.post.id}"
    

class PostReaction(BaseModel):
    REACTION_CHOICES = [
        ('UPVOTE', 'UPVOTE'),
        ('DOWNVOTE', 'DOWNVOTE'),   
        ('ANGRY', 'ANGRY'),
        ('SAD', 'SAD'),   
    ]

    user_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_reactions")
    user_that_react =  models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=20,null=False, blank=False, choices=REACTION_CHOICES)

    def __str__(self) -> str:
        return f"{self.user_post} {self.reaction}"
    


class CommentToPost(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comment")
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    user_that_comment =  models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    edited = models.BooleanField(default=False)


class CommentToPostImages(BaseModel):
    comment_to_post = models.ForeignKey(CommentToPost, on_delete=models.CASCADE, related_name="comment_to_post_images")
    post_image = models.ImageField(upload_to=post_images_upload_location, blank=True, null=True)

class CommentToPostReaction(BaseModel):

    REACTION_CHOICES = [
        ('UPVOTE', 'UPVOTE'),
        ('DOWNVOTE', 'DOWNVOTE'),   
        ('ANGRY', 'ANGRY'),
        ('SAD', 'SAD'),   
    ]

    comment_to_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comment_to_post_reaction")
    user_that_react =  models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=20,null=False, blank=False, choices=REACTION_CHOICES)

    def __str__(self) -> str:
        return f"{self.comment_to_post} {self.reaction}"
    
    






