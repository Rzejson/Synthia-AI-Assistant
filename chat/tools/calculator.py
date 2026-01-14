from base import BaseTool


class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return 'Calculator'

    @property
    def description(self) -> str:
        return 'A tool for simple mathematical operations.'

    @property
    def parameters(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'operation': {
                    'type': 'string',
                    'enum': ['add', 'subtract', 'multiply', 'divide'],
                    'description': 'The type of mathematical operation to perform.'
                },
                'x': {
                    'type': 'number',
                    'description': 'First number.'
                },
                'y': {
                    'type': 'number',
                    'description': 'Second number.'
                },
            },
            'required': ['operation', 'x', 'y']
        }

    def execute(self, **kwargs):
        x = kwargs.get('x')
        y = kwargs.get('y')
        operation = kwargs.get('operation')
        if operation == 'add':
            return str(x + y)
        if operation == 'subtract':
            return str(x - y)
        if operation == 'multiply':
            return str(x * y)
        if operation == 'divide':
            if y == 0:
                return "ERROR: You can't divide by zero!"
            else:
                return str(x / y)
