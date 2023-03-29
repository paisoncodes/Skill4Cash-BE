from django.urls import path

from .views import (
    BusinessProfileRetrieveUpdateView,
    ChangePassword,
    RegisterCustomer,
    ProfileRetrieveUpdateView,
    Login,
    RegisterServiceProvider,
    ResendOtp,
    SendPhoneNumberOtp,
    SetUpServiceProviderProfile,
    VerifyOtp,
    VerifyPhoneNumberOtp,
)

from social_auth.views import(
    GoogleSocialAuthView,
    FacebookSocialAuthView
)

urlpatterns = [
    path("customer/register/", RegisterCustomer.as_view()),
    path("profile/user/", ProfileRetrieveUpdateView.as_view()),
    path("profile/business/", BusinessProfileRetrieveUpdateView.as_view()),
    path("login/", Login.as_view()),
    path("verify-otp/", VerifyOtp.as_view()),
    path("resend-otp/", ResendOtp.as_view()),
    path("verify-phone-otp/", VerifyPhoneNumberOtp.as_view()),
    path("send-phone-otp/", SendPhoneNumberOtp.as_view()),
    path("change-password/", ChangePassword.as_view()),
    path("business/register/", RegisterServiceProvider.as_view()),
    path("setup-business-profile/", SetUpServiceProviderProfile.as_view()),
    path("google-auth/", GoogleSocialAuthView.as_view()),
]
