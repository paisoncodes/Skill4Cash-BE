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
    path("auth/customers/", CustomerRegisterGetAll.as_view()),
    path("auth/customers/<str:id>/", CustomerRetrieveUpdateDelete.as_view()),
    path("auth/sp/register/", ServiceProviderRegister.as_view()),
    path("auth/sp/<str:id>/", ServiceProviderRetrieveUpdateDelete.as_view()),
    path("auth/otp/update/", UpdatePhone.as_view(), name="UpdatePhone"),
    path("auth/otp/verification/", VerifyPhone.as_view(), name="VerifyPhone"),
    path("auth/customer/login/", CustomerLogin.as_view()),
    path("auth/service-provider/login/", ServiceProviderLogin.as_view()),
    path("auth/login/refresh/", RefreshToken.as_view()),
    path("auth/login/google/", GoogleLogin.as_view()),
    path("auth/verify-email/", VerifyEmail.as_view(), name="verify_email"),
    path("auth/change-password", ChangePassword.as_view()),
    path("auth/reset-password", ResetPassword.as_view()),
    path("auth/reset-password-email", ResetPasswordEmail.as_view()),
]
