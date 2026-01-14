from ..models import Conversation, Message, SystemPrompt
from ..serializers import ConversationSerializer, MessageSerializer
from .llm_factory import OpenAIService


class ConversationOrchestrator:
    """
    Central decision-making hub. Coordinate flows between the Django database and LLM services.
    Manage the chain of requests to LLM services.
    """
    def __init__(self, conversation):
        self.conversation = conversation

    def _classify_intent(self, message_text):
        """
        Download the appropriate prompt from the database, prepare a specific prompt format,
        send a query to the LLM service to recognize the intent.

        :param message_text: user message
        :type message_text: str
        :return: Response from the LLM service. Specifically, YES/NO for tool usage.
        :rtype: str
        """
        system_instruction = SystemPrompt.objects.get(name='Intentions').content
        system_prompt = [{"role": "system", "content": f'{system_instruction}: {message_text}'}]
        return OpenAIService(model_name='gpt-5-nano').get_response(system_prompt)

    def _get_normal_response(self):
        """
        A fallback method that returns the standard LLM response when tools are not required.
        Select the LLM model, prepare the prompt, download and prepare the conversation history,
        send a query containing the prompt and context to the LLM service.

        :return: None
        """
        if self.conversation.ai_model:
            model_name = self.conversation.ai_model.name
        else:
            model_name = 'gpt-5-nano'

        if self.conversation.system_prompt:
            system_instruction = self.conversation.system_prompt.content
            prompt_name_log = self.conversation.system_prompt.name
        else:
            system_instruction = "Jesteś Synthia, pomocna asystentka AI."
            prompt_name_log = "Standard (Hardcoded)"

        messages_query = Message.objects.filter(conversation=self.conversation).order_by('-timestamp')[:10]
        reversed_messages = reversed(messages_query)

        system_prompt = [{"role": "system", "content": system_instruction}]
        history_from_db = [{"role": msg.role, "content": msg.content} for msg in reversed_messages]
        context = system_prompt + history_from_db

        llm_service = OpenAIService(model_name=model_name)
        ai_content = llm_service.get_response(context)

        Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content=ai_content,
            ai_model_used=model_name,
            prompt_used_name=prompt_name_log
        )

    def handle_message(self, message_text):
        """
        Check the message intent, select a tool or get a response.

        :param message_text: user message
        :type message_text: str
        :return: None
        """
        intent = self._classify_intent(message_text)
        print(f'DEBUG: Intent recognized: {intent}')
        if intent.strip().upper() == 'YES':
            print("DEBUG: Trying to use a tool (not yet supported)")
            self._get_normal_response()
        else:
            self._get_normal_response()

