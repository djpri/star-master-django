"""
Management command to update search vectors for all questions.
"""
from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from questions.models import Question


class Command(BaseCommand):
    help = 'Update search vectors for all questions'

    def handle(self, *args, **options):
        self.stdout.write('Updating search vectors for questions...')

        updated = Question.objects.update(
            search_vector=SearchVector(
                'title', weight='A') + SearchVector('body', weight='B')
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated} question search vectors')
        )
