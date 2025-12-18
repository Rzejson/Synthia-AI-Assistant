from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializes message data for the API.
    """
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'timestamp', 'role', 'content']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializes conversation metadata.
    """
    class Meta:
        model = Conversation
        fields = ['id', 'topic', 'created_at']
