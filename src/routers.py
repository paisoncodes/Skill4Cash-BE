from rest_framework import routers

from authentication.views import (
    ImageUploadViewSet,
    ProfileViewSet,
    UserViewSet,
)
from chat.views import (
    ChatMessageViewSet,
    ConversationViewSet,
    FileViewSet,
    NotificationViewSet,
)
from services.views import CategoryViewSet, RatingViewSet, ScheduleViewSet
from utils.views import LgaViewSet, StateViewSet


router = routers.DefaultRouter()

router.register(r"users", UserViewSet, basename="user")
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"images", ImageUploadViewSet, basename="image")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"ratings", RatingViewSet, basename="rating")
router.register(r"schedules", ScheduleViewSet, basename="schedule")
router.register(r"states", StateViewSet, basename="state")
router.register(r"lgas", LgaViewSet, basename="lga")
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"chat", ChatMessageViewSet, basename="chat")
router.register(r"files", FileViewSet, basename="file")
router.register(r"notifications", NotificationViewSet, basename="notification")
