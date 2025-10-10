"""
Signal handlers for the answers app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import connection
from .models import StarAnswer, BasicAnswer


@receiver(post_save, sender=StarAnswer)
def update_star_answer_search_vector(sender, instance, **kwargs):
    """Update search vector when a STAR answer is saved."""
    # Skip if not using Postgres
    if connection.vendor != "postgresql":
        return

    # Only update if search_vector is empty or just created
    if instance.search_vector is None or kwargs.get("created", False):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE answers_answer
                SET search_vector =
                    setweight(to_tsvector('english', COALESCE(%s, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(%s, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(%s, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(%s, '')), 'A')
                WHERE id = %s
            """,
                [
                    instance.situation,
                    instance.task,
                    instance.action,
                    instance.result,
                    instance.pk,
                ],
            )


@receiver(post_save, sender=BasicAnswer)
def update_basic_answer_search_vector(sender, instance, **kwargs):
    """Update search vector when a basic answer is saved."""
    # Skip if not using Postgres
    if connection.vendor != "postgresql":
        return

    # Only update if search_vector is empty or just created
    if instance.search_vector is None or kwargs.get("created", False):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE answers_answer
                SET search_vector =
                    setweight(to_tsvector('english', COALESCE(%s, '')), 'A')
                WHERE id = %s
            """,
                [instance.text, instance.pk],
            )
