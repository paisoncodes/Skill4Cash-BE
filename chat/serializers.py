from django.conf import settings
from rest_framework import serializers
from .models import Conversation, ChatMessage, Notification, UploadedFile
    



# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB - 104857600
# 250MB - 214958080
# 500MB - 429916160

MAX_UPLOAD_SIZE = getattr(settings, 'MAX_FILE_UPLOAD_SIZE', 20971520)

class ConversationSerializer(serializers.ModelSerializer):
	chat_room = serializers.CharField(source="id")
	sender = serializers.CharField(source="user_one.__str__")
	reciever = serializers.CharField(source="user_two.__str__")
	class Meta:
	    model = Conversation
	    fields = ["chat_room", "sender", "reciever"]

class ChatMessageSerializer(serializers.ModelSerializer):
	profile_id = serializers.CharField(source='sender.id', read_only=True)
	profile_profile_pic = serializers.CharField(source='sender.profile_picture', read_only=True)
	profile_firstname = serializers.CharField(source='sender.first_name', read_only=True)
	profile_lastname = serializers.CharField(source='sender.last_name', read_only=True)
	profile_username = serializers.CharField(source='sender.user.username', read_only=True)

	class Meta:
		model = ChatMessage
		fields = [
			"id",
			"chats", 
			"file",
			"date_created", 
			"profile_id", 
			"profile_profile_pic", 
			"profile_firstname",
			"profile_lastname",
			"profile_username"
			]
		depth = 1

class NotificationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Notification
		fields = ["id", "title", "message", "reciever"]
		depth = 1

class FileSerializer(serializers.ModelSerializer):

    CHOICES = [
        ("picture","picture"),
        ("voice-note","voice-note"),
        ("document","document"),
        ("video", "video")
    ]
    
    file_type = serializers.ChoiceField(choices=CHOICES, write_only=True, required=True)
    conversation_id = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = UploadedFile
        fields = (
            "id", 
            'file_type', 
            "media", 
            "caption",
            "conversation_id"
        )

    def validate(self, attrs):

        media = attrs.get('media')

        if media and (media.size > MAX_UPLOAD_SIZE):
            raise serializers.ValidationError(
                {"media": "Please keep file size under 20MB"}
            )

        return attrs

