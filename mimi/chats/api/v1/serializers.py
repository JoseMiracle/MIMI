from mimi.chats.models import (
    Message,
    Room,
    RoomMembers,
    JoinRoomRequests
)

from rest_framework import serializers



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'edit_count',
            'message'
        ]

class EditOrDeleteMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'edit_count',
            'message'
        ]

    def update(self, instance, validated_data):
        instance.edit_count += 1 
        return super().update(instance, validated_data)
    

class RoomSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(min_length=5, allow_blank=False, required=True)
    class Meta:
        model = Room
        fields = [
            'id',
            'room_name',
            'description',
            'number_of_persons'
        ]

    
    def validate(self, attrs):
        room_name  = Room.objects.filter(room_name=attrs['room_name'])
        
        if room_name.exists():
            raise serializers.ValidationError({
                "error": f"room {attrs['room_name']} exists."
            }) 
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['room_creator_id'] = self.context['request'].user.id
        room_instance = super().create(validated_data)
       
        
        """This is for adding the creator of the room as a room member and making the room creator an admin"""
        room_members = RoomMembers.objects.create(
            room=room_instance,
            room_member_id=room_instance.room_creator_id,
            is_admin=True
            )
        return room_instance
        
class JoinRoomRequestSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.room_name', read_only=True)


    class Meta:
        model = JoinRoomRequests
        fields = [
            'room_name',
            'room',
            'room_request'
        ]


    def validate(self, attrs):
        is_room_request_exists = JoinRoomRequests.objects.filter(
            room=attrs['room'],
            user=self.context['request'].user
        ).exists()

        if is_room_request_exists:
            raise serializers.ValidationError(
                {
                    "error": "you have sent room request already"
                }
            )
        
        return attrs
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

class AcceptOrRejectUserRoomRequestSerializer(serializers.Serializer):
    decision = serializers.CharField(allow_blank=False)



class GetAllUsersInTheRoomSerializer(serializers.ModelSerializer):
    room_member = serializers.ReadOnlyField(source='room_member.username')
    room = serializers.ReadOnlyField(source='room.room_name')
   
    class Meta:
        model = RoomMembers
        fields = ['room_member', 'room']

class RemoveUserFromARoomSerializer(serializers.Serializer):
    username = serializers.CharField(allow_blank=False)
    room_name = serializers.CharField(allow_blank=False)
