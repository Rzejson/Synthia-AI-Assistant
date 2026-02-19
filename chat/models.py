from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
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


class PromptCategory(models.Model):
    """
    Represents a logical grouping for identity modules (e.g., Core Persona, Rules, Tools).
    Helps organize and filter prompt blocks in the admin panel.
    """
    name = models.CharField(max_length=50)
    key = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __str__(self):
        return f'{self.name} ({self.key})'


class IdentityModule(models.Model):
    """
    A modular block of text forming the core instructions or identity of the AI.
    Can be toggled on/off and reused across multiple Agent Modes.
    """
    name = models.CharField(max_length=50)
    content = models.TextField()
    category = models.ForeignKey(PromptCategory, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.category.name})'


class PersonalityTrait(models.Model):
    """
    Defines a specific behavioral attribute or characteristic (e.g., Humor, Empathy).
    """
    name = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AgentModeTrait(models.Model):
    """
    Intermediate 'through' model connecting an AgentMode with a PersonalityTrait.
    Stores the specific intensity value (0-10) for a trait in a given mode.
    """
    agent_mode = models.ForeignKey('AgentMode', on_delete=models.CASCADE)
    trait = models.ForeignKey(PersonalityTrait, on_delete=models.CASCADE)
    value = models.IntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(10)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['agent_mode', 'trait'],
                name='unique_agent_mode_trait',
                violation_error_message='This personality trait is already in this mode.'
            )
        ]


class AgentMode(models.Model):
    """
    Represents a distinct persona or configuration mode for the AI assistant.
    Acts as a central container that combines identity modules and personality traits.
    """
    name = models.CharField(max_length=50)
    key = models.CharField(max_length=20, unique=True)
    identity_modules = models.ManyToManyField(IdentityModule, blank=True)
    personality_traits = models.ManyToManyField(PersonalityTrait, through='AgentModeTrait', blank=True)
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.key})'

    def save(self, *args, **kwargs):
        if self.is_default:
            AgentMode.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    @staticmethod
    def get_default_mode():
        """
        Retrieves the default AgentMode from the database.
        Returns None if no default mode is set.
        """
        return AgentMode.objects.filter(is_default=True).first()

    def build_system_prompt(self):
        """
        Assembles the final system instructions for the LLM.
        Concatenates active identity modules and personality traits
        associated with this AgentMode.
        """
        identity_modules = self.identity_modules.filter(is_active=True)
        core_identity = ' '.join(module.content for module in identity_modules)
        traits = AgentModeTrait.objects.filter(agent_mode=self, trait__is_active=True)
        persona_traits = '\n'.join(f'- {trait.trait.name}: {trait.value}/10' for trait in traits)
        return f'{core_identity}\n\n Personality Traits:\n{persona_traits}'
