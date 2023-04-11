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
    path("reviews/", CreateReadReview.as_view(), name='review-list'),
    path("sp/reviews/", ReadSPReviews.as_view(), name='sp_review-list'),
    path("categories/", CreateReadCategory.as_view(), name="categories-list"),
    path("schedules/", CreateReadSchedule.as_view(), name='schedule-list'),
    path("sp/schedules/", ReadSPSchedules.as_view(), name='sp_schedule-list'),
    path("sp/schedules/<str:id>/",
         ReadUpdateDeleteSchedule.as_view(), name='sch_sp-detail'),
]
