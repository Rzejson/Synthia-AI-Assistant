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
                    'description': 'A short, concise TITLE of the task. '
                                   'Do NOT include date, time, or priority here.'
                },
                'description': {
                    'type': 'string',
                    'description': "If you don't have any additional, necessary information beyond the title itself, "
                                   "you MUST leave this field blank (null/empty). "
                                   "NEVER copy the contents of the 'content' field here."
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
        print(f"DEBUG TOOL INPUT: {kwargs}")
        payload = {k: v for k, v in kwargs.items() if v is not None}

        try:
            r = requests.post(
                'https://api.todoist.com/api/v1/tasks',
                headers={
                    'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                },
                json=payload
            )
            if r.status_code in [200, 201]:
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
        return "Retrieve active tasks."

    @property
    def parameters(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'filter': {
                    'type': 'string',
                    'description': 'Filter by any supported filter (the filter field only accepts native '
                                   'Todoist filters, e.g., "today", "tomorrow", "overdue"...). '
                                   'Multiple filters (using the comma , operator) are not supported. '
                                   'If the user asks to search for specific keywords, topics, '
                                   'or contents (e.g., "shopping"), YOU MUST leave this field empty, fetch all tasks, '
                                   'and find the matching tasks yourself.'
                },
            },
            'required': []
        }

    def execute(self, **kwargs) -> str:
        filters = kwargs.get('filter')
        all_tasks = []
        cursor = None
        if filters:
            try:
                r = requests.get(
                    'https://api.todoist.com/api/v1/tasks/filter',
                    headers={
                        'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                    },
                    params={'query': filters}
                )
                all_tasks.extend(r.json().get('results', []))
            except Exception as e:
                return f"System Error: {str(e)}"
        else:
            try:
                while True:
                    r = requests.get(
                        'https://api.todoist.com/api/v1/tasks',
                        headers={
                            'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                        },
                        params={
                            'cursor': cursor,
                            'limit': 20
                        }
                    )
                    response_data = r.json()
                    tasks = response_data.get('results', [])
                    all_tasks.extend(tasks)
                    next_cursor = response_data.get('next_cursor')
                    print(f"DEBUG: Page fetched. Cursor is: {cursor}")
                    if not next_cursor:
                        break
                    cursor = next_cursor
            except Exception as e:
                return f"System Error: {str(e)}"

        if r.status_code == 200:
            tasks = all_tasks
            tasks_list = []
            for task in tasks:
                due = 'no deadline'
                if task['due']:
                    due = task['due']['date']
                tasks_list.append(f"[ID:{task['id']}] {task['content']}, Due: {due}, Priority:{task['priority']}")
            formatted_tasks = "\n".join(tasks_list)
            return formatted_tasks
        else:
            return f"Error {r.status_code}: {r.text}"


class CloseTask(BaseTool):
    @property
    def name(self) -> str:
        return "CloseTask"

    @property
    def description(self) -> str:
        return "Mark task as completed / Close task. If you don't know the task ID, use GetTasks to check it."

    @property
    def parameters(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'task_id': {
                    'type': 'string',
                    'description':
                        "ID of the task to close. Required. Don't guess the ID if you don't know it, use GetTasks."
                },
            },
            'required': ['task_id']
        }

    def execute(self, **kwargs) -> str:
        task_id = kwargs.get('task_id')
        if not task_id:
            return "Error: Argument 'task_id' is missing. Please provide the ID of the task you want to close."

        try:
            r = requests.post(
                f'https://api.todoist.com/api/v1/tasks/{task_id}/close',
                headers={
                    'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                }
            )
            if r.status_code in [200, 204]:
                return f"Successfully closed task (ID: {task_id})."
            else:
                return f"Error closing task {task_id}: {r.status_code} - {r.text}"
        except Exception as e:
            return f"System Error: {str(e)}"


class UpdateTask(BaseTool):
    @property
    def name(self) -> str:
        return "UpdateTask"

    @property
    def description(self) -> str:
        return "Updates an existing task. If you don't know the task ID, use GetTasks to check it."

    @property
    def parameters(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'task_id': {
                    'type': 'string',
                    'description':
                        "ID of the task to update. Required. Don't guess the ID if you don't know it, use GetTasks."
                },
                'content': {
                    'type': 'string',
                    'description': 'Updated task content. Omit this field to keep it unchanged.'
                },
                'description': {
                    'type': 'string',
                    'description': 'Updated task description. Omit this field to keep it unchanged.'
                },
                'priority': {
                    'type': 'integer',
                    'description': 'Updated task priority (1-4, where 4 is highest). '
                                   'Omit this field to keep it unchanged.',
                    'enum': [1, 2, 3, 4],
                },
                'due_string': {
                    'type': 'string',
                    'description': 'Natural language date/time (e.g., "today", "tomorrow", "next Monday at 10am") '
                                   'or date string (RFC 3339 format or similar). Omit this field to keep it unchanged.'
                }

            },
            'required': ['task_id']
        }

    def execute(self, **kwargs) -> str:
        task_id = kwargs.get('task_id')
        payload = {k: v for k, v in kwargs.items() if v is not None and k != 'task_id'}
        if not payload:
            return "No data to update"
        try:
            r = requests.post(
                f'https://api.todoist.com/api/v1/tasks/{task_id}',
                headers={
                    'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                },
                json=payload
            )
            if r.status_code == 200:
                return f"Successfully updated task (ID: {task_id})."
            else:
                return f"Error updating task {task_id}: {r.status_code} - {r.text}"
        except Exception as e:
            return f"System Error: {str(e)}"


class DeleteTask(BaseTool):
    @property
    def name(self) -> str:
        return "DeleteTask"

    @property
    def description(self) -> str:
        return "Delete task (if unnecessary or outdated). If you don't know the task ID, use GetTasks to check it."

    @property
    def parameters(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'task_id': {
                    'type': 'string',
                    'description':
                        "ID of the task to delete. Required. Don't guess the ID if you don't know it, use GetTasks."
                },
            },
            'required': ['task_id']
        }

    def execute(self, **kwargs) -> str:
        task_id = kwargs.get('task_id')
        if not task_id:
            return "Error: Argument 'task_id' is missing. Please provide the ID of the task you want to delete."
        try:
            r = requests.delete(
                f"https://api.todoist.com/api/v1/tasks/{task_id}",
                headers={
                    'Authorization': f"Bearer {settings.TODOIST_API_KEY}"
                }
            )
            if r.status_code in [200, 204]:
                return f"Successfully deleted task (ID: {task_id})."
            else:
                return f"Error deleting task {task_id}: {r.status_code} - {r.text}"
        except Exception as e:
            return f"System Error: {str(e)}"
