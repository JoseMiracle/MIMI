from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class FriendRequest(BaseModel):
    FRIEND_REQUEST_CHOICES = (
        ('accepted', 'accepted'),
        ('pending', 'pending'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_friend_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_friend_requests")
    status = models.CharField(max_length=10, choices=FRIEND_REQUEST_CHOICES, default='pending')

    class Meta:
        unique_together = ('sender', 'receiver')



class Friends(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_friends")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_friends")

    class Meta:
        unique_together = ('user', 'friend')






