from django.utils import timezone
from chat.models import Message, SystemPrompt, AIModel
from chat.tools.registry import ToolRegistry
from chat.services.llm_factory import OpenAIService
from chat.rag import search_memory
import json


class ConversationOrchestrator:
    """
    Central decision-making hub. Coordinate flows between the Django database and LLM services.
    Manage the chain of requests to LLM services and tool execution.
    """
    def __init__(self, conversation):
        self.conversation = conversation
        self.tools_registry = ToolRegistry()

    def _prepare_context(self):
        """
        Prepare the full context for the LLM request.

        Resolves the AI model and system prompt by checking conversation-specific overrides first,
        then falling back to global active defaults from the database.
        Retrieves recent conversation history from the database.

        :return: A tuple containing: (list of message dicts for API, model name, prompt name for logging).
        :rtype: tuple[list, str, str]
        """

        if self.conversation.system_prompt:
            system_instruction = self.conversation.system_prompt.content
            prompt_name_log = self.conversation.system_prompt.name
        else:
            active_prompt_content, active_prompt_name = SystemPrompt.get_active_prompt(
                SystemPrompt.PromptType.MAIN_PERSONA
            )
            system_instruction = active_prompt_content
            prompt_name_log = active_prompt_name

        messages_query = Message.objects.filter(conversation=self.conversation).order_by('-timestamp')[:10]
        reversed_messages = reversed(messages_query)

        history_from_db = [{
            "role": msg.role,
            "content": f"[{timezone.localtime(msg.timestamp).strftime('%Y-%m-%d %H:%M')}] {msg.content}"
        } for msg in reversed_messages]

        return system_instruction, history_from_db, prompt_name_log

    def handle_message(self, message_text):
        model_name = AIModel.get_active_model_name(AIModel.TargetType.MAIN_CHAT)
        system_instruction, history, prompt_name_log = self._prepare_context()
        current_time = timezone.localtime()

        found_memories = search_memory(message_text)
        memory_context = '\n'.join([m.content for m in found_memories])

        full_system_content = f"{system_instruction}\n\n" \
                              f"Related Threads from Knowledge Base:\n{memory_context}\n\n" \
                              f"Current Date and Time: {current_time.strftime('%Y-%m-%d %H:%M')}"

        system_prompt = [{"role": "system", "content": full_system_content}]
        user_message = [{'role': 'user', 'content': message_text}]

        context = system_prompt + history + user_message
        tools_defs = self.tools_registry.get_tools_definitions()

        print(f"DEBUG: Starting Agent Loop with model: {model_name}")
        print(f"DEBUG: Tools available: {[t['function']['name'] for t in tools_defs]}")

        llm_service = OpenAIService(model_name=model_name)
        for i in range(5):
            response = llm_service.get_response(
                context=context,
                tools=tools_defs
            )
            context.append(response)

            if response.tool_calls:
                print(f"DEBUG: Attempt to use a tool detected\n\nDEBUG: {response.tool_calls}")
                tool_call = response.tool_calls[0]
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    func_args = {}
                tool = self.tools_registry.get_tool(func_name)
                if tool:
                    result = tool.execute(**func_args)
                else:
                    result = f"Error: Tool {func_name} not found."
                tool_message = {
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': str(result)
                }
                context.append(tool_message)
            else:
                Message.objects.create(
                    conversation=self.conversation,
                    role='assistant',
                    content=response.content,
                    ai_model_used=model_name,
                    prompt_used_name=prompt_name_log
                )
                return response.content
