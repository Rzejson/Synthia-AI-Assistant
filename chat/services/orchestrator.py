from django.utils import timezone
from chat.models import Message, AIModel, AgentMode
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

        Dynamically builds the system instructions by retrieving the default AgentMode
        (including active identity modules and personality traits). Falls back to a
        hardcoded prompt if no default mode is set. Retrieves recent conversation history.

        :return: A tuple containing: (system instruction string, list of history message dicts,
        prompt/mode name for logging, context message limit, RAG results limit).
        :rtype: tuple[str, list, str, int, int]
        """

        agent_mode = AgentMode.get_default_mode()
        if agent_mode:
            system_instruction = agent_mode.build_system_prompt()
            prompt_name_log = agent_mode.name
            tool_limit = agent_mode.max_tool_iteration_limit
            context_limit = agent_mode.context_message_limit
            rag_limit = agent_mode.rag_results_limit
        else:
            system_instruction = 'You are Synthia, a helpful AI assistant.'
            prompt_name_log = 'Hardcoded Fallback'
            tool_limit = 5
            context_limit = 10
            rag_limit = 3

        messages_query = Message.objects.filter(conversation=self.conversation).order_by('-timestamp')[:context_limit]
        reversed_messages = reversed(messages_query)

        history_from_db = [{
            "role": msg.role,
            "content": f"[{timezone.localtime(msg.timestamp).strftime('%Y-%m-%d %H:%M')}] {msg.content}"
        } for msg in reversed_messages]

        return system_instruction, history_from_db, prompt_name_log, tool_limit, rag_limit

    def handle_message(self, message_text):
        model_name = AIModel.get_active_model_name(AIModel.TargetType.MAIN_CHAT)
        system_instruction, history, prompt_name_log, tool_limit, rag_limit = self._prepare_context()
        current_time = timezone.localtime()

        found_memories = search_memory(message_text, limit=rag_limit)
        memory_context = '\n'.join([m.content for m in found_memories])

        full_system_content = f"{system_instruction}\n\n" \
                              f"Related Threads from Knowledge Base:\n{memory_context}\n\n" \
                              f"Current Date and Time: {current_time.strftime('%Y-%m-%d %H:%M')}"

        system_prompt = [{"role": "system", "content": full_system_content}]
        user_message = [{'role': 'user', 'content': message_text}]

        context = system_prompt + history + user_message
        tools_defs = self.tools_registry.get_tools_definitions()

        llm_service = OpenAIService(model_name=model_name)

        for i in range(tool_limit):
            print(f'DEBUG: Loop rotation {i}')
            response = llm_service.get_response(
                context=context,
                tools=tools_defs
            )
            context.append(response)

            if response.tool_calls:
                print(f'DEBUG: Parallel Tools Check {len(response.tool_calls)}')
                for tool_call in response.tool_calls:
                    func_name = tool_call.function.name
                    print(f'DEBUG: TOOLS: {func_name}')
                    try:
                        func_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        func_args = {}
                    print(f'DEBUG: TOOLS ARGS: {func_args}')
                    tool = self.tools_registry.get_tool(func_name)
                    if tool:
                        result = tool.execute(**func_args)
                        print(f'DEBUG: Tool result: {result}')
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

        return 'System: Maximum tool iteration limit reached. Process aborted.'
