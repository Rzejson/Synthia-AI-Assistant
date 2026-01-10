from rest_framework import viewsets
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services import OpenAIService, ConversationOrchestrator


class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that provides CRUD operations (Create, Read, Update, Delete) for Conversation objects.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing messages.
    Creating a new message automatically triggers a response from the LLM.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        serializer.save(role='user')
        orchestrator = ConversationOrchestrator(conversation)
        orchestrator.handle_message(serializer.validated_data['content'])

