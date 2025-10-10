from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.utils import timezone
from questions.models import Question

User = settings.AUTH_USER_MODEL


class AnswerQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        """Return answers visible to the user"""
        if not user or not user.is_authenticated:
            # Public answers on approved public questions
            return self.filter(
                is_public=True,
                question__is_public=True,
                question__status="APPROVED",
            )

        # Own answers + public answers on visible questions
        return self.filter(
            models.Q(user=user)
            | models.Q(
                is_public=True,
                question__in=Question.objects.visible_to_user(user),
            )
        )


class AnswerManager(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def visible_to_user(self, user):
        return self.get_queryset().visible_to_user(user)


class Answer(models.Model):
    ANSWER_TYPE_STAR = "STAR"
    ANSWER_TYPE_BASIC = "BASIC"
    ANSWER_TYPE_CHOICES = [
        (ANSWER_TYPE_STAR, "STAR"),
        (ANSWER_TYPE_BASIC, "Basic"),
    ]

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="answers"
    )
    # user-scoped; public visibility is subject to question approval rules too
    is_public = models.BooleanField(default=False)
    answer_type = models.CharField(max_length=10, choices=ANSWER_TYPE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Search vector for combined searchable text for answers (maintained from
    # subclass fields via signal/management command)
    search_vector = SearchVectorField(null=True, editable=False)

    objects = AnswerManager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
            models.Index(fields=["answer_type"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.answer_type} answer by {self.user} on {self.question_id}"
        )


class StarAnswer(Answer):
    # Multi-table inheritance: creates an implicit OneToOneField to Answer
    situation = models.TextField()
    task = models.TextField()
    action = models.TextField()
    result = models.TextField()

    class Meta:
        verbose_name = "STAR Answer"
        verbose_name_plural = "STAR Answers"

    def save(self, *args, **kwargs):
        self.answer_type = self.ANSWER_TYPE_STAR
        # enforce required fields presence — though DB-level NOT NULL already
        # ensures it
        super().save(*args, **kwargs)


class BasicAnswer(Answer):
    text = models.TextField()

    class Meta:
        verbose_name = "Basic Answer"
        verbose_name_plural = "Basic Answers"

    def save(self, *args, **kwargs):
        self.answer_type = self.ANSWER_TYPE_BASIC
        super().save(*args, **kwargs)
