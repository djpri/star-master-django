"""
Management command to update search vectors for all answers.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Update search vectors for all answers'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write('Updating search vectors for STAR answers...')

            # Update STAR answers using raw SQL
            cursor.execute("""
                UPDATE answers_answer
                SET search_vector = 
                    setweight(to_tsvector('english', COALESCE(answers_staranswer.situation, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(answers_staranswer.task, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(answers_staranswer.action, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(answers_staranswer.result, '')), 'A')
                FROM answers_staranswer
                WHERE answers_answer.id = answers_staranswer.answer_ptr_id
            """)
            star_count = cursor.rowcount

            self.stdout.write('Updating search vectors for Basic answers...')

            # Update Basic answers using raw SQL
            cursor.execute("""
                UPDATE answers_answer
                SET search_vector = 
                    setweight(to_tsvector('english', COALESCE(answers_basicanswer.text, '')), 'A')
                FROM answers_basicanswer
                WHERE answers_answer.id = answers_basicanswer.answer_ptr_id
            """)
            basic_count = cursor.rowcount

        total_updated = star_count + basic_count

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {star_count} STAR answers and {basic_count} basic answers '
                f'(total: {total_updated})'
            )
        )
