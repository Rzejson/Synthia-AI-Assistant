from chat.models import Conversation, Message, SystemPrompt, AIModel
from chat.tools.registry import ToolRegistry
from chat.services.llm_factory import OpenAIService
import json


class ConversationOrchestrator:
    """
    Central decision-making hub. Coordinate flows between the Django database and LLM services.
    Manage the chain of requests to LLM services and tool execution.
    """
    def __init__(self, conversation):
        self.conversation = conversation
        self.tools_registry = ToolRegistry()

    def _classify_intent(self, message_text):
        """
        Retrieve the active intent classification prompt, construct the system message,
        and query the LLM to determine if tools are needed.

        :param message_text: The user's input message.
        :type message_text: str
        :return: 'YES' if tool usage is detected, 'NO' otherwise.
        :rtype: str
        """
        system_instruction = SystemPrompt.get_active_prompt(SystemPrompt.PromptType.INTENT_CLASSIFIER)[0]
        model_name = AIModel.get_active_model_name(AIModel.TargetType.INTENT_CLASSIFIER)
        system_prompt = [{"role": "system", "content": f'{system_instruction}: {message_text}'}]
        response_obj = OpenAIService(model_name=model_name).get_response(system_prompt)
        return response_obj.content

    def _prepare_context(self):
        """
        Prepare the full context for the LLM request.

        Resolves the AI model and system prompt by checking conversation-specific overrides first,
        then falling back to global active defaults from the database.
        Retrieves recent conversation history from the database.

        :return: A tuple containing: (list of message dicts for API, model name, prompt name for logging).
        :rtype: tuple[list, str, str]
        """
        if self.conversation.ai_model:
            model_name = self.conversation.ai_model.api_name
        else:
            model_name = AIModel.get_active_model_name(AIModel.TargetType.MAIN_CHAT)

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

        system_prompt = [{"role": "system", "content": system_instruction}]
        history_from_db = [{"role": msg.role, "content": msg.content} for msg in reversed_messages]
        context = system_prompt + history_from_db

        return context, model_name, prompt_name_log

    def _get_normal_response(self):
        """
        A fallback method that returns the standard LLM response when tools are not required.

        Selects the LLM model, prepares the context (prompt + history), sends the query,
        saves the assistant's response to the database, and returns the content.

        :return: The content of the assistant's response.
        :rtype: str
        """
        context, model_name, prompt_name_log = self._prepare_context()

        llm_service = OpenAIService(model_name=model_name)
        response_msg = llm_service.get_response(context)

        Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content=response_msg.content,
            ai_model_used=model_name,
            prompt_used_name=prompt_name_log
        )

        return response_msg.content

    def _handle_tool_usage(self):
        """
        Orchestrate the tool execution flow.

        1. Prepares context including tool definitions.
        2. Gets the initial response from LLM (deciding which tool to call).
        3. Executes the selected tool logic.
        4. Appends the tool result to the context.
        5. Generates the final natural language response based on the tool result.
        6. Saves the interaction to the database.

        :return: The final response content after tool execution.
        :rtype: str
        """
        context, model_name, prompt_name_log = self._prepare_context()

        tools_defs = self.tools_registry.get_tools_definitions()

        llm_service = OpenAIService(model_name=model_name)
        response_msg = llm_service.get_response(context, tools=tools_defs)

        print(f'DEBUG Selected tool: {response_msg.tool_calls}')

        if response_msg.tool_calls:
            tool_call = response_msg.tool_calls[0]
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
            tool_info_prompt = {
                "role": "system",
                "content": f"Tool {func_name} executed. Result: {result}. "
                           f"Note: If the result indicates an error, inform the user about it truthfully."
            }
            context.append(tool_info_prompt)
            final_response = llm_service.get_response(context)

            Message.objects.create(
                conversation=self.conversation,
                role='assistant',
                content=final_response.content,
                ai_model_used=model_name,
                prompt_used_name=prompt_name_log
            )
            return final_response.content
        else:
            Message.objects.create(
                conversation=self.conversation,
                role='assistant',
                content=response_msg.content,
                ai_model_used=model_name,
                prompt_used_name=prompt_name_log
            )
            return response_msg.content

    def handle_message(self, message_text):
        """
        Main entry point for processing a user message.
        Classifies the intent and delegates execution to either the tool handler or the standard response handler.

        :param message_text: The content of the message received from the user.
        :type message_text: str
        :return: The final text response from the assistant to be sent back to the user.
        :rtype: str
        """
        intent = self._classify_intent(message_text)
        print(f'DEBUG: Intent recognized: {intent}')
        if intent.strip().upper() == 'YES':
            print(f"DEBUG: Executing tool flow for intent: {intent}")
            return self._handle_tool_usage()
        else:
            return self._get_normal_response()
