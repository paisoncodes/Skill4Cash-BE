from django.urls import path

from .views import (
    CustomerRegisterGetAll,
    CustomerRetrieveUpdateDelete,
    DecodeToken,
    PopulateCategory,
    ServiceProviderDocumentUpload,
    ServiceProviderLogin,
    ServiceProviderGalleryUpload,
    ServiceProviderRegister,
    ServiceProviderRetrieveUpdateDelete,
    TestImageUploadView,
    VerifyEmail,
    GetOTP,
    VerifyPhone,
    UpdatePhone,
    ChangePassword,
    ResetPassword,
    ResetPasswordEmail,
    CustomerLogin,
    RefreshToken,
    SPLogin
)

from social_auth.views import(
    GoogleSocialAuthView,
    FacebookSocialAuthView
)

urlpatterns = [
    path("auth/customers/", CustomerRegisterGetAll.as_view()),
    path("auth/customers/<str:id>/", CustomerRetrieveUpdateDelete.as_view()),
    path("auth/service-provider/register/", ServiceProviderRegister.as_view()),
    path("auth/service-provider/<str:id>/", ServiceProviderRetrieveUpdateDelete.as_view()),
    path("auth/otp/", GetOTP.as_view(), name='GetOTP'),
    path("auth/update-phone/", UpdatePhone.as_view(), name="UpdatePhone"),
    path("auth/verify-phone/", VerifyPhone.as_view(), name="VerifyPhone"),
    path("auth/customer/login/", CustomerLogin.as_view()),
    # path("auth/service-provider/login/", ServiceProviderLogin.as_view()),
    path("auth/login/refresh/", RefreshToken.as_view()),
    path("auth/verify-email/", VerifyEmail.as_view(), name="verify_email"),
    path("auth/change-password/", ChangePassword.as_view()),
    path("auth/reset-password/", ResetPassword.as_view()),
    path("auth/reset-password-email/", ResetPasswordEmail.as_view()),
    path("auth/decode/", DecodeToken.as_view()),
    path("auth/test-upload/", TestImageUploadView.as_view()),
    path("auth/service-provider-gallery-update/", ServiceProviderGalleryUpload.as_view()),
    path("auth/service-provider-document-update/", ServiceProviderDocumentUpload.as_view()),
    path("auth/facebook/login/", FacebookSocialAuthView.as_view()),
    path("auth/google/login/", GoogleSocialAuthView.as_view()),
    path("util/category-upload/", PopulateCategory.as_view()),
    path("auth/sp/login", SPLogin.as_view()),
]
