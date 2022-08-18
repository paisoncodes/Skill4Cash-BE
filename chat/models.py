from django.db import models
from authentication.models import User
from django.utils import timezone
import uuid
class Chat(models.Model):
    initiator = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="initiator_chat"
    )
    acceptor = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="acceptor_name"
    )
    short_id = models.CharField(max_length=255, default=uuid.uuid4, unique=True)


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
