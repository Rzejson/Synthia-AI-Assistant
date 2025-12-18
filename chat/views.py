from rest_framework import viewsets
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that provides CRUD operations (Create, Read, Update, Delete) for Conversation objects.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that provides CRUD operations (Create, Read, Update, Delete) for Messages objects.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
