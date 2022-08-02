from django.urls import path

from .views import (
    CustomerRegisterGetAll,
    CustomerRetrieveUpdateDelete,
    ServiceProviderLogin,
    ServiceProviderRegister,
    ServiceProviderRetrieveUpdateDelete,
    VerifyEmail,
    VerifyPhone,
    UpdatePhone,
    GoogleLogin,
    ChangePassword,
    ResetPassword,
    ResetPasswordEmail,
    CustomerLogin,
    RefreshToken,
)


urlpatterns = [
    path("customers/", CustomerRegisterGetAll.as_view()),
    path("customers/<str:id>/", CustomerRetrieveUpdateDelete.as_view()),
    path("sp/register/", ServiceProviderRegister.as_view()),
    path("sp/<str:id>/", ServiceProviderRetrieveUpdateDelete.as_view()),
    path("otp/update/", UpdatePhone.as_view(), name="UpdatePhone"),
    path("otp/verification/", VerifyPhone.as_view(), name="VerifyPhone"),
    path("customer/login/", CustomerLogin.as_view()),
    path("service-provider/login/", ServiceProviderLogin.as_view()),
    path("login/refresh/", RefreshToken.as_view()),
    path("login/google/", GoogleLogin.as_view()),
    path("verify-email/", VerifyEmail.as_view(), name="verify_email"),
    path("change-password", ChangePassword.as_view()),
    path("reset-password", ResetPassword.as_view()),
    path("reset-password-email", ResetPasswordEmail.as_view()),
]
