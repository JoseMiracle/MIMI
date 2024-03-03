from rest_framework import generics, permissions, status
from mimi.accounts.api.v1.serializers import(
    RegistrationSerializer,
    SignInSerializer,
    ChangePasswordSerializer,
    UpdateProfileSerializer,
    ActivateAccountSerializer,
    BlockUserSerializer,
    OtpResetPaswordSerializer,
    UserProfileSerializer
)


from django.contrib.auth import get_user_model
from rest_framework.response import Response

User  = get_user_model()


class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ActivateAccountAPIView(generics.GenericAPIView):

    serializer_class = ActivateAccountSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.kwargs, context={"uid": kwargs["uidb64"], "token": kwargs["token"]})
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)

    
class SignInAPIVIew(generics.GenericAPIView):
    serializer_class = SignInSerializer
    permission_classes = (permissions.AllowAny,)


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            
            return Response(serializer.data)

class ChangePasswordAPIView(generics.GenericAPIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = self.request.user
            user.set_password(serializer.validated_data["confirm_password"])
            user.save()
            return Response({"message": "password changed"}, status=status.HTTP_200_OK)

class UserProfileAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UpdateProfileAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateProfileSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

class BlockUserAPIView(generics.ListCreateAPIView):
    serializer_class = BlockUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class OtpForResetPasswordAPIView(generics.GenericAPIView):
    serializer_class = OtpResetPaswordSerializer

    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            
            return Response({"message": "password changed"}, status=status.HTTP_200_OK)
