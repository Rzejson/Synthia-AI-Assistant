from openai import OpenAI
from django.conf import settings
from chat.models import Memory
from pgvector.django import CosineDistance

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_embedding(text):
    embedding = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return embedding.data[0].embedding


def search_memory(query, limit=3):
    query_vector = get_embedding(query)
    memories = Memory.objects.alias(
        distance=CosineDistance('embedding', query_vector)
    ).order_by('distance')[:limit]

    return memories
