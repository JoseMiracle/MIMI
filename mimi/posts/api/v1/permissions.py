from rest_framework.permissions import BasePermission, SAFE_METHODS
from mimi.posts.models import Post
from mimi.accounts.models import BlockedList
from django.contrib.auth import get_user_model

User = get_user_model()

# class IsPostOwner(BasePermission):
#     message = "you can only update your post"
    
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated



class IsUserBlocked(BasePermission):
    message = "You can't view user's post as you are blocked"

    def has_permission(self, request, view):
        user = User.objects.filter(username=view.kwargs["username"]).first()
        
        if user is not None:
            is_other_user_blocked_by_user = BlockedList.objects.filter(user=user, other_user=request.user)
            return not is_other_user_blocked_by_user.exists()
      

