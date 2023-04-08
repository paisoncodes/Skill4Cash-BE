
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/dm/<str:chat_room>/', consumers.DmConsumer.as_asgi()),
    path('ws/notifications/', consumers.Notification.as_asgi())
]