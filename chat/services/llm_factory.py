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
    def get_response(self, context, tools=None):
        """
        Send context and tool to LLM and return text response.

        :param context: List of message dictionaries (role/content) or specific prompt data.
        :param tools: Tool to use, default is None
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

    def get_response(self, context, tools=None):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=context,
                tools=tools
            )
            return response.choices[0].message
        except Exception as e:
            print(f'OpenAI Error: {e}')
            return 'Error! There was a problem connecting to LLM. Please try again later.'

    def transcribe_audio(self, audio_file):
        """
        Transcribes audio file using OpenAI Whisper model.

        :param audio_file: file-like object (binary) containing the audio
        :return: Transcribed text (str)
        """
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        return transcript
