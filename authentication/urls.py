from django.urls import path

from .views import (
    ChangePassword,
    RegisterCustomer,
    ProfileRetrieveUpdateView,
    Login,
    ResendOtp,
    SendPhoneNumberOtp,
    VerifyOtp,
    VerifyPhoneNumberOtp,
)

from social_auth.views import(
    GoogleSocialAuthView,
    FacebookSocialAuthView
)

urlpatterns = [
    path("customer/register/", RegisterCustomer.as_view()),
    path("profile/customer/", ProfileRetrieveUpdateView.as_view()),
    path("login/", Login.as_view()),
    path("verify-otp/", VerifyOtp.as_view()),
    path("resend-otp/", ResendOtp.as_view()),
    path("verify-phone-otp/", VerifyPhoneNumberOtp.as_view()),
    path("send-phone-otp/", SendPhoneNumberOtp.as_view()),
    path("change-password/", ChangePassword.as_view()),
]
