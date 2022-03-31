from django.urls import path

from .views import (
    CreateReadReview,
    ReadSPReviews,
    PickCategory,  
)

urlpatterns = [
    path("category/", PickCategory.as_view(), name="categories")
]