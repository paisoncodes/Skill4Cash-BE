from django.urls import path

from .views import (
    CreateReadReview,
    CreateReadSchedule,
    ReadSPReviews,
    CreateReadCategory,
    ReadSPSchedules,
    ReadUpdateDeleteSchedule,

    PopulateData,

)

urlpatterns = [
    path("review/", CreateReadReview.as_view(), name='review-list'),
    path("reviews/", ReadSPReviews.as_view(), name='sp_review-list'),
    path("category/", CreateReadCategory.as_view(), name="categories-list"),
    path("schedule/", CreateReadSchedule.as_view(), name='schedule-list'),
    path("schedules/", ReadSPSchedules.as_view(), name='sp_schedule-list'),
    path("schedule/service-provider/<str:id>/",
         ReadUpdateDeleteSchedule.as_view(), name='sch_sp-detail'),
    path('populate-data/', PopulateData.as_view()),
]
