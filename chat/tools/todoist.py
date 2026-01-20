import requests
from django.conf import settings
from chat.tools.base import BaseTool


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
                    'description': 'Human-readable representation of the due date or in YYYY-MM-DD format'
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
        return "Get all active tasks from a to-do list."

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
