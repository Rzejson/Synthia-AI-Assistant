from rest_framework import viewsets
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services import OpenAIService


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
        2. Retrieves the active AI Model and System Prompt from the conversation settings.
        3. Retrives the last 10 messages from the conversation history.
        4. Constructs a prompt including the system instruction and history.
        5. Sends the context to the LLM Service.
        5. Saves the AI's response and audit logs (model used, prompt name) as a new message.

        :param serializer: The validated serializer instance containing the new message data.
        :return: None
        """
        conversation = serializer.validated_data['conversation']
        serializer.save(role='user')

        if conversation.ai_model:
            model_name = conversation.ai_model.name
        else:
            model_name = 'gpt-5-nano'

        if conversation.system_prompt:
            system_instruction = conversation.system_prompt.content
            prompt_name_log = conversation.system_prompt.name
        else:
            system_instruction = "Jesteś Synthia, pomocna asystentka AI."
            prompt_name_log = "Standard (Hardcoded)"

        messages_query = Message.objects.filter(conversation=conversation).order_by('-timestamp')[:10]
        reversed_messages = reversed(messages_query)

        system_prompt = [{"role": "system", "content": system_instruction}]
        history_from_db = [{"role": msg.role, "content": msg.content} for msg in reversed_messages]
        context = system_prompt + history_from_db

        llm_service = OpenAIService(model_name=model_name)
        ai_content = llm_service.get_response(context)

        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_content,
            ai_model_used=model_name,
            prompt_used_name=prompt_name_log
        )
