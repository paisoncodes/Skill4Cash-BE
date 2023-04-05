from . serializers import ConversationSerializer, ChatMessageSerializer, NotificationSerializer
from . models import Conversation, ChatMessage, Notification
from rest_framework.permissions import IsAuthenticated
from authentication.models import UserProfile
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

class Chat(generics.GenericAPIView):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()
    permission_classes = [ IsAuthenticated ]

    def get(self, request, other_user_id=None):
        sender = UserProfile.objects.get(user=request.user)
        recipient = UserProfile.objects.get(user_id=other_user_id)

        room_name = Conversation.create_if_not_exists(sender, recipient)
        serializer = self.get_serializer(room_name, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChatByConversationListAPIView(generics.GenericAPIView):
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()
    permission_classes = [ IsAuthenticated ]

    def get(self, request, conversation):
        
        dm_message = ChatMessage.objects.select_related(
                    "conversation","sender__user","file"
                    ).filter(conversation__id=conversation)
        
        if dm_message.exists():
            serializer = self.get_serializer(dm_message, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message":'No Chats Yet'},status=status.HTTP_200_OK)

class RecentDmList(generics.GenericAPIView):
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()
    permission_classes = [ IsAuthenticated ]

    def get(self, request, user_id):  
        recent_dms = ChatMessage.objects.select_related("conversation","sender__user","file")\
                    .filter(sender__id=user_id).order_by('-date_created')

        conversation_ids = []
        recent_chats = []

        if recent_dms.exists():
            for _ in recent_dms:
                if _.conversation_id not in conversation_ids:
                    recent_chats.append(_.id)
                    conversation_ids.append(_.conversation_id)
            messages = ChatMessage.objects.\
                        select_related("conversation","sender__user","file")\
                        .filter(id__in=recent_chats).order_by("-date_created")

            serializer = ChatMessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message":'No Chats Yet'},status=status.HTTP_200_OK)

class NotificationListAPIView(generics.ListAPIView):
    queryset = Notification.objects.select_related("reciever__user").all()
    serializer_class = NotificationSerializer

class NotificationDetailAPIView(generics.RetrieveAPIView):
    queryset = Notification.objects.select_related("reciever__user").all()
    serializer_class = NotificationSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

class NotificationForUserListAPIView(generics.GenericAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):

        notify = Notification.objects.select_related(
                    'reciever__user').filter(reciever__user_id=user_id)
        
        if notify.exists():
            serializer = self.get_serializer(notify, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message":'No Chats Yet'}, status=status.HTTP_200_OK)
        
chat = Chat.as_view()
chat_list_con = ChatByConversationListAPIView.as_view()
chat_recent_dms = RecentDmList.as_view()
notify_list = NotificationListAPIView.as_view()
notify_detail = NotificationDetailAPIView.as_view()
notify_by_user = NotificationForUserListAPIView.as_view()