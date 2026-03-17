from chat.tools.base import BaseTool
from chat.rag import get_embedding
from chat.models import Memory


class SaveMemory(BaseTool):
    @property
    def name(self) -> str:
        return 'SaveMemory'

    @property
    def description(self) -> str:
        return ("Record in memory (RAG) an important fact about the user, "
                "facts about the user's life, preferences, friends, etc.")

    @property
    def parameters(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'fact': {
                    'type': 'string',
                    'description': "An important fact about the user, a note specifying who and what the fact concerns."
                                   "Must be written as an objective, third-person statement (e.g., 'User has a brother "
                                   "named John' instead of 'My brother is John')."
                },
            },
            'required': ['fact']
        }

    def execute(self, **kwargs) -> str:
        fact = kwargs.get('fact')
        if not fact:
            return "Error: Argument 'fact' is missing."
        try:
            vector = get_embedding(fact)
            Memory.objects.create(
                content=fact,
                embedding=vector
            )
            return f"Successfully saved to long-term memory: {fact}"
        except Exception as e:
            return f"Error saving memory: {str(e)}"
