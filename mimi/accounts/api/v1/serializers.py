from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from mimi.accounts.mails import account_activation 
from django.db import transaction
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from mimi.accounts.mails.tokens import account_activation_token
from mimi.accounts.models import BlockedList


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'image',
            'username',
            'email',
            'password',
            'date_of_birth'
        ]
        
    
    def validate(self, attrs):
        return super().validate(attrs)
    
    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.is_active = False
        user.save()
        
        

        """
            Activating account
        """
        
        current_site_domain = self.context["request"].META['HTTP_HOST']
        account_activation.send_activation_email(user,current_site_domain)

        return user
    


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "image"]


class ActivateAccountSerializer(serializers.Serializer):
    
    def validate(self, attrs):
        user_id = force_str(urlsafe_base64_decode(self.context["uid"]))
        token = self.context["token"]
        
        user = User.objects.filter(id=user_id).first() 
        if user is None:
            raise serializers.ValidationError("user doesn't exist")
        if account_activation_token.check_token(user, token) is False:
           raise serializers.ValidationError("wrong token or token expired")
        
        elif (user is not None and account_activation_token.check_token(user, token)):
            user.is_active = True
            user.save()
            attrs["message"] = "Account Activated"
            return attrs
        
class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs) :
        """
        This is for validating the values provided by user to login
        """
        user = User.objects.filter(email=attrs["email"]).first()

        error = {}
        if (user and user.check_password(attrs["password"])) and (user.is_active == True):
            return user

        else:
            error["credential_error"] = "Please recheck the credentials provided."
            raise serializers.ValidationError(error)

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {"refresh": str(refresh), "access_token": str(refresh.access_token)}
    



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8, write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        """
        This is for validating the values the user provides in order to change their password
        """
        user = self.context["request"].user

        if user.check_password(attrs["old_password"]) is False:
            raise serializers.ValidationError({
                "status": "false",
                "message": "Please provide the old password"
            })

        
        elif attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "status": "false",
                    "message": "new password not same as confirm password"
                }
            )

        elif user.check_password(attrs["new_password"]):
            raise serializers.ValidationError({
                "status": "false",
                "message": "new password can't be same as old password"
            })

        elif (attrs["old_password"] != attrs["new_password"]) and (
            attrs["new_password"] == attrs["confirm_password"]
        ):
            attrs["status"] = "true"
            return attrs
        


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "address",
            "image"
        ]

class BlockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedList
        fields = ["blocked_user"]

    
    def create(self, validated_data):
        BlockedList.objects.create(
                                    user =self.context["request"].user,
                                    blocked_user=validated_data["blocked_user"],
                                    )
        return validated_data


class OtpResetPaswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        user_email = User.objects.filter(email=attrs["email"]).first()
        
        if user_email is None:
            raise serializers.ValidationError({
                "status": "false",
                "message": "email address is invalid or don't exist"
            })
        

        






