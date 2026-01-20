from chat.tools.calculator import CalculatorTool
from chat.tools.todoist import CreateTask, GetTasks, CloseTask


class ToolRegistry:
    def __init__(self):
        calc = CalculatorTool()
        add_todo = CreateTask()
        close_task = CloseTask()
        get_tasks_todo = GetTasks()

        self.tools = {
            calc.name: calc,
            add_todo.name: add_todo,
            close_task.name: close_task,
            get_tasks_todo.name: get_tasks_todo
        }

    def get_tool(self, name: str):
        return self.tools.get(name)

    def get_tools_definitions(self) -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            } for tool in self.tools.values()
        ]
