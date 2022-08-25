from django.urls import path
from .views import GetChat

urlpatterns = [
    path("chats/all", GetChat.as_view(), name="get-chats"),
]
