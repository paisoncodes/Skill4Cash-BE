from django.urls import path

from .views import (
    Customer,
    CustomerRetrieveUpdateDelete,
    ServiceProvider,
    ServiceProviderRetrieveUpdateDelete
)


urlpatterns = [
    path("user/", Customer.as_view()),
    path("user/<str:id>/", CustomerRetrieveUpdateDelete.as_view()),
    path("sp_user/", ServiceProvider.as_view()),
    path("sp_user/<str:id>/", ServiceProviderRetrieveUpdateDelete.as_view())
]