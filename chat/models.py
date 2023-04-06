from django.utils.translation import gettext_lazy as _
from authentication.models import UserProfile
from utils.models import BaseModel
from typing import Optional, Any
from django.db.models import Q
from django.db import models

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/chat/file_type/<filename>
    return f"chat/{instance.file_type}/{filename}"

class UploadedFile(models.Model):

    class FileType(models.TextChoices):
        PICTURE = "PICTURE", _("Picture")
        VOICE_NOTE = "VOICE-NOTE", _("Voice-Note")
        DOCUMENT = "DOCUMENT", _("Document")
        VIDEO = "VIDEO", _("Video")
    
    file_type = models.CharField(max_length=15, choices=FileType.choices, default=FileType.PICTURE)
    media = models.FileField(help_text='Files', upload_to=upload_path, blank=True, null=True)
    caption = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

class Conversation(BaseModel):
    user_one = models.ForeignKey(
        UserProfile, 
        related_name='conversation_user_one',
        verbose_name='User1',
        on_delete=models.CASCADE
    )
    user_two = models.ForeignKey(
        UserProfile,
        related_name='conversation_user_two',
        verbose_name='User2',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (('user_one', 'user_two'), ('user_one', 'user_two'))
        indexes = [ models.Index(fields=['user_one', 'user_two'])]

    def __str__(self):
        return f"{self.user_one} meets {self.user_two}"

    @staticmethod
    def conversation_exists(user1: UserProfile, user2: UserProfile) -> Optional[Any]:
        return Conversation.objects.select_related('user_one__user', 'user_two__user').filter(
                Q(user_one=user1, user_two=user2) | Q(user_one=user2, user_two=user1)
            ).first()

    @staticmethod
    def create_if_not_exists(user1:UserProfile, user2: UserProfile):
        response = Conversation.conversation_exists(user1, user2)
        if not response:
            return Conversation.objects.create(user_one=user1, user_two=user2)
        return response

class ChatMessage(BaseModel):
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="Author",
        related_name='from_user',
        db_index=True
    )
    chats = models.TextField(
        'Messages', 
        max_length=1000, 
        blank=True, 
        null=True
    )
    file = models.OneToOneField(
        UploadedFile, 
        related_name='file_chat', 
        on_delete=models.CASCADE, 
        blank=True, null=True
    )


    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return f"{self.chats}"
    
    def create_file(self, sender=None, media=None, caption=None, conversation_id=None, file_type=None):
        try:
            file = UploadedFile.objects.create(
                media=media, caption=caption, file_type=file_type)
            con = Conversation.objects.select_related(
                "user_one__user", "user_two__user").get(id=conversation_id)
            return ChatMessage.objects.create(
                conversation=con, sender=sender, file=file
            )
        except:
            return None

class Notification(BaseModel):

    class MobleDevice(models.TextChoices):
        IOS_DEVICE = "IOS", _("Ios")
        ANDRIOD_DEVICE = "ANDRIOD", _("Android")

    reciever = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='user_notifications'
    )
    message = models.TextField(
        default='Messages',
        blank=False,
        null=False 
    )
    title = models.CharField(
        default="Title",
        max_length=100, 
        blank=False, 
        null=False
    )
    platform = models.CharField(
        max_length=20, 
        choices=MobleDevice.choices, 
        default=MobleDevice.ANDRIOD_DEVICE
    )
    token = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_created']
        indexes = [ 
            models.Index(fields=['title']),
            models.Index(fields=['platform'])
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)
        data = {
            "reciever_id": str(self.reciever.id),
            "message":self.message,
            "title": self.title
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
                'notify', {
                    'type': 'send_notification',
                    'notifications': json.dumps(data)
                }
            )

