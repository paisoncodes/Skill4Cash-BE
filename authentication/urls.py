from django.urls import path

from .views import (
    CustomerRegisterGetAll,
    CustomerRetrieveUpdateDelete,
    ServiceProviderRegister,
    ServiceProviderRetrieveUpdateDelete,
    VerifyEmail,
    VerifyPhone,
    UpdatePhone,
    GoogleLogin,
    ChangePassword,
    ResetPassword,
    ResetPasswordEmail,

    PopulateUser,
    PopulateSP
)


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)


urlpatterns = [
    path("customers/", CustomerRegisterGetAll.as_view()),
    path("customers/<str:id>/", CustomerRetrieveUpdateDelete.as_view()),
    path("sp/register/", ServiceProviderRegister.as_view()),
    path("sp/<str:id>/", ServiceProviderRetrieveUpdateDelete.as_view()),
    path('otp/update/', UpdatePhone.as_view(), name='UpdatePhone'),
    path("otp/verification/", VerifyPhone.as_view(), name='VerifyPhone'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("login/google/", GoogleLogin.as_view()),
    path('verify-email/', VerifyEmail.as_view(), name="verify_email"),
    path("change-password", ChangePassword.as_view()),
    path("reset-password", ResetPassword.as_view()),
    path("reset-password-email", ResetPasswordEmail.as_view()),

    # populating
    path('populate-cus/', PopulateUser.as_view(),),
    path('populate-sp/', PopulateSP.as_view(),)
]
