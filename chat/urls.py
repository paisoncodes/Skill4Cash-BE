from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.start_chat, name="start_convo"),
    path("<int:chat_id>/", views.get_conversation, name="get_conversation"),
    path("", views.conversations, name="conversations"),
]
