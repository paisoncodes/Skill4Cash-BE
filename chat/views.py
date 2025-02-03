from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.db.models import Q
from .serializers import (
    ConversationSerializer,
    ChatMessageSerializer,
    NotificationSerializer,
    FileSerializer,
)
from .models import Conversation, ChatMessage, Notification, UploadedFile
from authentication.models import UserProfile


class ConversationViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        "retrieve_conversation": ConversationSerializer,
    }
    queryset = Conversation.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @action(detail=False, methods=["get"], url_path="chat/(?P<other_user_id>[^/.]+)")
    def retrieve_conversation(self, request, other_user_id=None):
        sender = UserProfile.objects.get(user=request.user)
        recipient = UserProfile.objects.get(user_id=other_user_id)

        room_name = Conversation.create_if_not_exists(sender, recipient)
        serializer = self.get_serializer(room_name, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatMessageViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        "list_by_conversation": ChatMessageSerializer,
        "recent_dms": ChatMessageSerializer,
    }
    queryset = ChatMessage.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @action(
        detail=False, methods=["get"], url_path="conversation/(?P<conversation>[^/.]+)"
    )
    def list_by_conversation(self, request, conversation=None):
        dm_message = ChatMessage.objects.select_related(
            "conversation", "sender__user", "file"
        ).filter(conversation__id=conversation)

        if dm_message.exists():
            serializer = self.get_serializer(dm_message, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "No Chats Yet"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="recent-dms/(?P<user_id>[^/.]+)")
    def recent_dms(self, request, user_id=None):
        con = set(
            Conversation.objects.select_related("user_one__user", "user_two__user")
            .filter(Q(user_one__id=user_id) | Q(user_two__id=user_id))
            .values_list("id", flat=True)
        )
        recent_dms = ChatMessage.objects.select_related(
            "conversation", "sender__user", "file"
        ).filter(conversation_id__in=con)

        conversation_ids = []
        recent_chats = []

        if recent_dms.exists():
            for _ in recent_dms:
                if _.conversation_id not in conversation_ids:
                    recent_chats.append(_.id)
                    conversation_ids.append(_.conversation_id)
            messages = ChatMessage.objects.select_related(
                "conversation", "sender__user", "file"
            ).filter(id__in=recent_chats)

            serializer = ChatMessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "No Chats Yet"}, status=status.HTTP_200_OK)


class FileViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        "upload": FileSerializer,
    }
    queryset = UploadedFile.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @action(detail=False, methods=["post"])
    def upload(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            profile = UserProfile.objects.get(user=request.user)

            media = serializer.validated_data.get("media")
            caption = serializer.validated_data.get("caption")
            file_type = serializer.validated_data.get("file_type")
            conversation_id = serializer.validated_data.get("conversation_id")

            if files := ChatMessage.create_file(
                self,
                sender=profile,
                media=media,
                conversation_id=conversation_id,
                file_type=file_type,
                caption=caption,
            ):
                serializer = ChatMessageSerializer(files, many=False)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"message": "Invalid ID"}, status=status.HTTP_404_NOT_FOUND)


class NotificationViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        "list": NotificationSerializer,
        "retrieve": NotificationSerializer,
        "list_by_user": NotificationSerializer,
    }
    queryset = Notification.objects.select_related("reciever__user").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        notification = self.get_object()
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="user/(?P<user_id>[^/.]+)")
    def list_by_user(self, request, user_id=None):
        notify = Notification.objects.select_related("reciever__user").filter(
            reciever__user_id=user_id
        )

        if notify.exists():
            serializer = self.get_serializer(notify, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "No Notifications Yet"}, status=status.HTTP_200_OK)
