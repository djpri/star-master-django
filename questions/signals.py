"""
Signal handlers for the questions app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from django.db import connection
from .models import Question


@receiver(post_save, sender=Question)
def update_question_search_vector(sender, instance, **kwargs):
    """Update search vector when a question is saved."""
    # Skip if not using Postgres
    if connection.vendor != 'postgresql':
        return

    # Only update if search_vector is empty to avoid infinite recursion
    if instance.search_vector is None or kwargs.get('created', False):
        Question.objects.filter(pk=instance.pk).update(
            search_vector=SearchVector(
                'title', weight='A') + SearchVector('body', weight='B')
        )
