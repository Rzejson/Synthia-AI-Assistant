from django.contrib import admin
from .models import Conversation, Message, AIProvider, AIModel, SystemPrompt

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(AIProvider)
admin.site.register(AIModel)
admin.site.register(SystemPrompt)