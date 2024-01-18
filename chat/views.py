"""Views for Chats"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Chat
from chat import serializers
from django.shortcuts import render


class ChatViewSet(viewsets.ModelViewSet):
    """Manage chats Chat APIs"""
    serializer_class = serializers.ChatDetailSerializer
    queryset = Chat.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return serializers.ChatSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Create a new chat"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update a chat"""
        print(serializer.validated_data)
        serializer.save(user=self.request.user)


def simple_chat_view(request):
    return render(request, 'chat/simple_chat.html', {})
