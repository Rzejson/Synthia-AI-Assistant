import requests
import re
from django.conf import settings
from chat.tools.base import BaseTool
from chat.models import SystemPrompt
from chat.services.llm_factory import OpenAIService


class CreateTask(BaseTool):
    @property
    def name(self) -> str:
        return "CreateTask"

    @property
    def description(self) -> str:
        return "Create a new task on to-do list / Todoist"

    @property
    def parameters(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'content': {
                    'type': 'string',
                    'description': 'The core task content ONLY (e.g., "Buy milk"). '
                                   'Do NOT include date, time, or priority here.'
                },
                'description': {
                    'type': 'string',
                    'description': 'Additional details or context. Do NOT include date, time, or priority here.'
                },
                'priority': {
                    'type': 'integer',
                    'description': 'Priority level. 4 is HIGHEST (Red/Urgent), 1 is LOWEST (Natural). Default is 1.',
                    'enum': [1, 2, 3, 4],
                },
                'due_string': {
                    'type': 'string',
                    'description': 'Natural language date/time (e.g., "today", "tomorrow", "next Monday at 10am") '
                                   'or date string. Extract strictly from user prompt.'
                }

            },
            'required': ['content']
        }

    def execute(self, **kwargs) -> str:
        content = kwargs.get('content')
        description = kwargs.get('description')
        priority = kwargs.get('priority')
        due_string = kwargs.get('due_string')

        print(f"DEBUG TOOL INPUT: {kwargs}")

        payload = {'content': content}
        if description:
            payload['description'] = description
        if priority:
            payload['priority'] = priority
        if due_string:
            payload['due_string'] = due_string

        try:
            r = requests.post(
                'https://api.todoist.com/rest/v2/tasks',
                headers={
                    'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                },
                json=payload
            )
            if r.status_code == 200:
                data = r.json()
                return f"Task created. ID: {data['id']}, Content: {data['content']}, " \
                       f"Priority: {data.get('priority', 'Default')}"
            else:
                return f"Error {r.status_code}: {r.text}"
        except Exception as e:
            return f"System Error: {str(e)}"


class GetTasks(BaseTool):
    @property
    def name(self) -> str:
        return "GetTasks"

    @property
    def description(self) -> str:
        return "Retrieve active tasks. [READ-ONLY] This tool DOES NOT remove or modify any tasks."

    @property
    def parameters(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'filter': {
                    'type': 'string',
                    'description':
                        "Filter criteria, e.g., 'today', 'overdue', 'priority 1'. Leave empty for all active tasks."
                },
            },
            'required': []
        }

    def execute(self, **kwargs) -> str:
        filters = kwargs.get('filter')
        payload = {'filter': filters} if filters else None

        print(f"DEBUG TOOL INPUT: {kwargs}")

        try:
            r = requests.get(
                'https://api.todoist.com/rest/v2/tasks',
                headers={
                    'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                },
                params=payload
            )
        except Exception as e:
            return f"System Error: {str(e)}"
        if r.status_code == 200:
            tasks = r.json()
            return "\n".join(
                [
                    f"ID:{task['id']}, {task['content']}, {task['due']['date'] if task['due'] else 'No deadline.'}, "
                    f"Priority:{task['priority']}" for task in tasks
                ]
            )
        else:
            return f"Error {r.status_code}: {r.text}"


class CloseTask(BaseTool):
    @property
    def name(self) -> str:
        return "CloseTask"

    @property
    def description(self) -> str:
        return "[ACTION] Permanently removes/closes a task from the list. " \
               "Use this whenever user wants to delete/finish something."

    @property
    def parameters(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'task_name': {
                    'type': 'string',
                    'description':
                        "The content/name of the task to close (e.g. 'Buy milk'). Required."
                },
            },
            'required': ['task_name']
        }

    def execute(self, **kwargs) -> str:
        task_name = kwargs.get('task_name')
        if not task_name:
            return "Error: Argument 'task_name' is missing. Please provide the name of the task you want to close."

        print(f"DEBUG TOOL INPUT: {kwargs}")

        try:
            r = requests.get(
                'https://api.todoist.com/rest/v2/tasks',
                headers={
                    'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                }
            )
            if r.status_code != 200:
                return f"Error {r.status_code}: {r.text}"
            tasks_dict = r.json()
        except Exception as e:
            return f"System Error: {str(e)}"

        tasks = "\n".join(
            [f"ID:{task['id']}, {task['content']}" for task in tasks_dict]
        )

        print(f'DEBUG TASKS: {tasks}')

        system_prompt = SystemPrompt.get_active_prompt('tool_todoist')[0]
        context = [{
            "role": "system",
            "content": f"{system_prompt}\n\n"
                       f"User Query: '{task_name}'\n\n"
                       f"Tasks List:\n{tasks}"
        }]

        llm_service = OpenAIService(model_name='gpt-3.5-turbo')
        raw_task_id = llm_service.get_response(context).content.strip()

        print(f'DEBUG AI FOUND ID: {raw_task_id}')

        match = re.search(r'\d+', raw_task_id)
        if match:
            task_id = match.group()
        else:
            return f"I couldn't find a task matching '{task_name}' on your list (AI returned: {raw_task_id})."

        real_task_content = "Unknown task"
        for t in tasks_dict:
            if str(t['id']) == str(task_id):
                real_task_content = t['content']
                break

        try:
            r = requests.post(
                f'https://api.todoist.com/rest/v2/tasks/{task_id}/close',
                headers={
                    'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                }
            )
            if r.status_code == 204:
                return f"Successfully closed task '{real_task_content}' (ID: {task_id})."
            else:
                return f"Error closing task {task_id}: {r.status_code} - {r.text}"
        except Exception as e:
            return f"System Error: {str(e)}"
