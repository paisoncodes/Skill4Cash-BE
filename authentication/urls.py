from django.urls import path

from .views import (
    CustomerRegisterGetAll,
    CustomerRetrieveUpdateDelete,
    ServiceProviderRegister,
    ServiceProviderRetrieveUpdateDelete,
    VerifyEmail,
    GoogleLogin
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
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("login/google/", GoogleLogin.as_view()), 
    path('verify-email/', VerifyEmail.as_view(), name="verify_email")
]