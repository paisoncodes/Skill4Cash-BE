from django.urls import path

from authentication.views import PopulateCategory

from .views import (
    CreateReadReview,
    CreateReadSchedule,
    ReadSPReviews,
    ReadCategory,
    ReadSPSchedules,
    ReadUpdateDeleteSchedule,

)

urlpatterns = [
    path("reviews/", CreateReadReview.as_view(), name='review-list'),
    path("sp/reviews/", ReadSPReviews.as_view(), name='sp_review-list'),
    path("get-categories/", ReadCategory.as_view(), name="categories-list"),
    path("add-categories/", PopulateCategory.as_view(), name="categories-list"),
    path("schedules/", CreateReadSchedule.as_view(), name='schedule-list'),
    path("sp/schedules/", ReadSPSchedules.as_view(), name='sp_schedule-list'),
    path("sp/schedules/<str:id>/",
         ReadUpdateDeleteSchedule.as_view(), name='sch_sp-detail'),
]
