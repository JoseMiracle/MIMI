from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_("first name"), max_length=150, blank=False, null=False)
    email = models.EmailField(_("email address"), blank=False, null=False)
    image = models.ImageField(upload_to='images/', blank=True)
    address = models.CharField(_("address"), max_length=500, blank=True)
    date_of_birth = models.DateTimeField(blank=False, null=True)
    gender = models.CharField(max_length=10, default="other")
    bio = models.CharField(max_length=500, blank=True, null=True)


    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email","first_name"]

    def __str__(self):
        return self.username
    
class UsersBlockedByUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="blocked_other_users")
    other_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_other_user_blocked = models.BooleanField(default=False)


class OTP(models.Model):
    otp = models.CharField(max_length=10)
    email = models.EmailField(max_length=60, blank=False, null=False)


