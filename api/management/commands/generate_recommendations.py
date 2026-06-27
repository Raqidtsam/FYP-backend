from django.core.management.base import BaseCommand
from api.recommendation_engine import engine


class Command(BaseCommand):
    help = 'Generate AI-powered investment recommendations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--district_id',
            type=int,
            help='Generate for specific district only',
        )

    def handle(self, *args, **kwargs):
        district_id = kwargs.get('district_id')

        self.stdout.write('Generating AI recommendations...')
        count = engine.generate_recommendations(district_id)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated {count} recommendations')
        )