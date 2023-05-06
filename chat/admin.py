from django.contrib import admin
from .models import Conversation, ChatMessage, Notification


admin.site.register(Conversation)
admin.site.register(Notification)
admin.site.register(ChatMessage)