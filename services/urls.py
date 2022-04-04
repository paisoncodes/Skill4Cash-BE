from django.urls import path

from .views import (
    CreateReadReview,
    ReadSPReviews,
    CreateReadCategory,  
)

urlpatterns = [
    path("category/", CreateReadCategory.as_view(), name="categories")
]