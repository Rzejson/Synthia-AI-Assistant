from django.core.management.base import BaseCommand
from chat.rag import get_embedding
from chat.models import Memory


class Command(BaseCommand):
    def handle(self, *args, **options):
        fact_to_remember = options['fact']
        vector = get_embedding(fact_to_remember)
        Memory.objects.create(
            content=fact_to_remember,
            embedding=vector
        )
        print('Knowledge added.')

    def add_arguments(self, parser):
        parser.add_argument('fact', type=str, help='The text you want the Assistant to remember.')
