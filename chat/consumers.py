from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from . models import ChatMessage, Conversation
from authentication.models import UserProfile
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import json

class DmConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_group_name = self.scope['url_route']['kwargs']['chat_room']
		self.user = self.scope['user']
		self.conversation = await self.get_conversation()
		self.user_profile = await self.get_profile()
		
		await self.channel_layer.group_add(self.room_group_name, self.channel_name)
		await self.accept()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

	async def receive(self, text_data):

		# recieving message from frontend and parsing it via json
		text_data_json = json.loads(text_data)
		message = text_data_json['message']

		# saving an instance of a chat
		chat = await self.create_message(message)
		
		await self.channel_layer.group_send(
				self.room_group_name,
				{
				'type': 'chat_message',
				'message': message,
				'first_name':self.user_profile.first_name,
				'last_name': self.user_profile.last_name,
				'profile_pic': self.user_profile.profile_picture,
				'profile_id': str(self.user_profile.id),
				'time_created': str(chat.date_created),
				'chat_id': str(chat.id),
				})

	async def chat_message(self, event):
		message = event['message']
		first_name = event['first_name']
		last_name = event['last_name']
		profile_pic = event['profile_pic']
		profile_id = event['profile_id']
		time_created = event['time_created']
		chat_id = event['chat_id']

		await self.send(text_data=json.dumps({
					'message': message,
					'first_name':first_name,
					'last_name': last_name,
					'profile_pic': profile_pic,
					'profile_id': profile_id,
					'time_created': time_created,
					'chat_id': chat_id,
				}))

	@database_sync_to_async
	def create_message(self, message):
		message_obj = ChatMessage.objects.create(
							conversation=self.conversation,
							sender=self.user_profile,
							chats=message)
		return message_obj

	@database_sync_to_async
	def get_conversation(self):
		# Get the conversation from the database
		return Conversation.objects.select_related(
			'user_one__user', 'user_two__user').get(id=self.room_group_name)

	@database_sync_to_async
	def get_profile(self):
		# Get the profile of a user from the database
		return UserProfile.objects.select_related(
			'user', 'state', 'lga__state').get(user=self.user)


class Notification(WebsocketConsumer):
	def connect(self):
		self.room_name = 'notify'
		async_to_sync(self.channel_layer.group_add)(
				self.room_name, self.channel_name
			)
		self.accept()

	def disconnect(self, close_code):
		self.close(close_code)

	def send_notification(self, event):
		self.send(event.get('notifications'))
