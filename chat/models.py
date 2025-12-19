from django.db import models
from django.utils import timezone


class AIProvider(models.Model):
    """
    Represents an AI service provider.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class AIModel(models.Model):
    """
    Represents a specific AI model version available from a provider.
    """
    name = models.CharField(max_length=50)
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} ({self.provider})'


class SystemPrompt(models.Model):
    """
    Represents a predefined system instruction (persona) for the AI.
    """
    name = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.name


class Conversation(models.Model):
    """
    A model representing a single conversation (thread) with an AI assistant.
    It stores metadata (topic, start date of the conversation) and configuration (active model/prompt).
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
    A model representing a single message within a conversation.
    It contains the message content, author, creation date and audit logs (which model generated it).
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
