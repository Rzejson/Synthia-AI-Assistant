from django.db import models
from django.utils import timezone
from pgvector.django import VectorField


class AIProvider(models.Model):
    """
    Represents an AI service provider (e.g., OpenAI, Anthropic).
    Used to group models by their source.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class AIModel(models.Model):
    """
    Represents a specific version of an LLM available in the system.
    Used for configuring conversation settings.
    """
    name = models.CharField(max_length=50)
    api_name = models.CharField(max_length=50)
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)

    class TargetType(models.TextChoices):
        MAIN_CHAT = 'main_chat', 'Main chat'
        INTENT_CLASSIFIER = 'intent_classifier', 'Intent classifier'
        TOOL_TODOIST = 'tool_todoist', 'Todoist'

    target_type = models.CharField(
        max_length=50,
        choices=TargetType.choices,
        default=TargetType.MAIN_CHAT
    )

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.provider})'

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to enforce exclusivity.

        If 'is_active' is set to True, this method automatically deactivates (sets is_active=False)
        all other AIModel records of the same 'target_type'.
        """
        if self.is_active:
            AIModel.objects.filter(target_type=self.target_type, is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    @staticmethod
    def get_active_model_name(target_type):
        active_model = AIModel.objects.filter(target_type=target_type, is_active=True).first()
        if active_model:
            return active_model.api_name
        else:
            return 'gpt-3.5-turbo'


class SystemPrompt(models.Model):
    """
    Configuration model for system instructions.

    Supports different categories of prompts (e.g., Main Persona, Intent Classifier).
    Enforces a logic where only one prompt of a given type can be active globally at a time.
    """
    name = models.CharField(max_length=100)
    content = models.TextField()

    class PromptType (models.TextChoices):
        MAIN_PERSONA = 'main_persona', 'Main persona'
        INTENT_CLASSIFIER = 'intent_classifier', 'Intent classifier'
        TOOL_TODOIST = 'tool_todoist', 'Todoist'

    target_type = models.CharField(
        max_length=50,
        choices=PromptType.choices,
        default=PromptType.MAIN_PERSONA
    )

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to enforce exclusivity.

        If 'is_active' is set to True, this method automatically deactivates (sets is_active=False)
        all other SystemPrompt records of the same 'target_type'.
        """
        if self.is_active:
            SystemPrompt.objects.filter(target_type=self.target_type, is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    @staticmethod
    def get_active_prompt(target_type='main_persona'):
        """
        Retrieves the content and name of the currently active prompt for a given type.

        :param target_type: The category of the prompt to retrieve (from PromptType choices).
        :return: A tuple (content, name). Returns a hardcoded fallback tuple if no active prompt is found.
        :rtype: tuple[str, str]
        """
        active_prompt = SystemPrompt.objects.filter(target_type=target_type, is_active=True).first()
        if active_prompt:
            return active_prompt.content, active_prompt.name
        else:
            return 'You are Synthia, the helpful AI assistant.', 'Hardcoded Fallback'


class Conversation(models.Model):
    """
    Represents a single conversation thread with the user.

    Acts as a container for messages and holds configuration overrides.
    If 'system_prompt' is set here, it overrides the global active SystemPrompt.
    """
    topic = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    system_prompt = models.ForeignKey(SystemPrompt, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """Returns a readable representation of the object (subject and date)."""
        local_timestamp = timezone.localtime(self.created_at)
        return f"{self.topic} ({local_timestamp.strftime('%Y-%m-%d %H:%M')})"


class Message(models.Model):
    """
    Represents a single message within a conversation.

    Stores the content, role (user/assistant), and audit metadata (which model and prompt
    were actually used to generate this specific response).
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    ai_model_used = models.CharField(max_length=50, null=True, blank=True)
    prompt_used_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        """Clear presentation of the message (date, author, content)."""
        local_timestamp = timezone.localtime(self.timestamp)
        return f"{local_timestamp.strftime('%Y-%m-%d %H:%M')} {self.role}: {self.content[:50]}..."


class Memory(models.Model):
    content = models.TextField()
    embedding = VectorField(dimensions=1536)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]