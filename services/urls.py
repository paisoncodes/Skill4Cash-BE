from django.urls import path

from .views import (
    CreateReadReview,
    CreateReadSchedule,
    ReadSPReviews,
    CreateReadCategory,
    ReadSPSchedules,
    ReadUpdateDeleteSchedule,  
)

urlpatterns = [
    path("category/", CreateReadCategory.as_view(), name="categories"),
    # path("review/", CreateReadReview.as_view()),
    # path("reviews/", ReadSPReviews.as_view()),
    # path("schedule/", CreateReadSchedule.as_view()),
    # path("schedules/", ReadSPSchedules.as_view()),
    # path("schedule/service-provider/", ReadUpdateDeleteSchedule.as_view())
]