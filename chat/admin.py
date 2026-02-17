from django.contrib import admin
from .models import (
    Conversation, Message, AIProvider, AIModel, SystemPrompt, Memory, PromptCategory,
    IdentityModule, PersonalityTrait, AgentModeTrait, AgentMode
)

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(AIProvider)
admin.site.register(AIModel)
admin.site.register(SystemPrompt)
admin.site.register(Memory)


@admin.register(PromptCategory)
class PromptCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'description')


@admin.register(IdentityModule)
class IdentityModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'content')


@admin.register(PersonalityTrait)
class PersonalityTraitAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ['name']


class AgentModeTraitInline(admin.TabularInline):
    model = AgentModeTrait
    extra = 1
    autocomplete_fields = ['trait']


@admin.register(AgentMode)
class AgentModeAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'is_default', 'ai_model')
    inlines = [AgentModeTraitInline]
    filter_horizontal = ('identity_modules',)
