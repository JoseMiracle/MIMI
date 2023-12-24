from django.urls import path
from mimi.accounts.api.v1.views import (
    RegistrationAPIView,
    SignInAPIVIew,
    ChangePasswordAPIView,
    UpdateProfileAPIView,
    ActivateAccountAPIView,
    BlockUserAPIView
)

app_name = "accounts"

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view(), name='registration'),
    path('activate/<uidb64>/<token>/', ActivateAccountAPIView.as_view(), name='activate'),
    path('sign-in/', SignInAPIVIew.as_view(), name='sign-in'),
    path('block-user/', BlockUserAPIView.as_view(), name='block_user'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('update-profile/', UpdateProfileAPIView.as_view(), name="update-profile"),

]