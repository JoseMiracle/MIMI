from rest_framework.permissions import BasePermission
from mimi.chats.models import RoomMembers, Room

class IsRoomAdmin(BasePermission): 
  
    message = "Not a member of the room or room doesn't exist"
    

    def has_permission(self, request, view):
        return super().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
      room_name = view.kwargs['room_name']
        
        # Check if the room exists
      room = Room.objects.filter(room_name=room_name).first()
      if not room:
            return False  # or handle the case as appropriate
        
      member = RoomMembers.objects.filter(room=room, room_member=request.user).first()
        
        # Check if room_member is None before accessing attributes
      if member and member.is_admin:
         return True
      return False
