from rest_framework import serializers
from .models import Conversation, ChatMessage, Notification, UploadedFile
    

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