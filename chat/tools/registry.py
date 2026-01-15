from chat.tools.calculator import CalculatorTool


class ToolRegistry:
    def __init__(self):
        calc = CalculatorTool()
        self.tools = {calc.name: calc}

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
