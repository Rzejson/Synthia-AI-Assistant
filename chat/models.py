from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """
    A model representing a single conversation (thread) with an AI assistant.
    It stores metadata such as the subject and start date of the conversation.
    """
    topic = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Returns a readable representation of the object (subject and date)."""
        local_timestamp = timezone.localtime(self.created_at)
        return f"{self.topic} ({local_timestamp.strftime('%Y-%m-%d %H:%M')})"


class Message(models.Model):
    """
    A model representing a single message within a conversation.
    It contains the message content, author, and creation date.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Clear presentation of the message (date, author, content)."""
        local_timestamp = timezone.localtime(self.timestamp)
        return f"{local_timestamp.strftime('%Y-%m-%d %H:%M')} {self.role}: {self.content[:50]}..."
