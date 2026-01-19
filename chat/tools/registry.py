from chat.tools.calculator import CalculatorTool
from chat.tools.todoist import CreateTask


class ToolRegistry:
    def __init__(self):
        calc = CalculatorTool()
        add_todo = CreateTask()

        self.tools = {
            calc.name: calc,
            add_todo.name: add_todo
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
