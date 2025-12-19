from django.conf import settings
from rest_framework import viewsets
import openai
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
    API endpoint for managing messages.
    Creating a new message automatically triggers a response from the OpenAI LLM.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        """
        Overrides the default create behavior to integrate with OpenAI.

        Process flow:
        1. Saves the user's message to the database.
        2. Retrives the last 10 messages from the conversation history.
        3. Constructs a prompt including the system instruction and history.
        4. Sends the request to OpenAI API.
        5. Saves the AI's response (or an error message) as a new message.

        :param serializer: The validated serializer instance containing the new message data.
        :return: None
        """
        conversation = serializer.validated_data['conversation']
        serializer.save(role='user')

        messages_query = Message.objects.filter(conversation=conversation).order_by('-timestamp')[:10]
        reversed_messages = reversed(messages_query)

        system_prompt = [{"role": "system", "content": "Jesteś Synthią, pomocnym asystentem AI."}]
        history_from_db = [{"role": msg.role, "content": msg.content} for msg in reversed_messages]
        message_history = system_prompt + history_from_db

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        try:
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=message_history
            )

            ai_content = response.choices[0].message.content
        except Exception as e:
            print(f'OpenAI Error: {e}')
            ai_content = 'ERROR! There was a problem connecting to LLM. Please try again later.'

        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_content
        )
