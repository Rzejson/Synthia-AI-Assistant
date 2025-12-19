from django.conf import settings
from abc import ABC, abstractmethod
import openai


class BaseLLMService(ABC):
    """
    Abstract Base Class defining the contract for all LLM services.
    Ensures that any new AI provider (Gemini, Anthropic, etc.) implements
    the required methods.
    """
    @abstractmethod
    def get_response(self, context):
        """
        Sends the context to the LLM and returns the text response.
        :param context: List of message dictionaries (role/content) or specific prompt data.
        :return: String containing the AI's response.
        """
        pass


class OpenAIService(BaseLLMService):
    """
    Implementation of LLM Service using OpenAI API.
    """
    def __init__(self, model_name='gpt-5-nano'):
        self.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model_name

    def get_response(self, context):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=context
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f'OpenAI Error: {e}')
            return 'ERROR! There was a problem connecting to LLM. Please try again later.'
