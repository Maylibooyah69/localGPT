"""Serializer for Chat apis"""
from rest_framework import serializers

from core.models import Chat


class ChatSerializer(serializers.ModelSerializer):
    """Serializer for Chat objects"""

    class Meta:
        model = Chat
        fields = ['id', 'title', 'summary']
        read_only_fields = ['id',]


class ChatDetailSerializer(ChatSerializer):
    class Meta(ChatSerializer.Meta):
        fields = ChatSerializer.Meta.fields + ['content',]
