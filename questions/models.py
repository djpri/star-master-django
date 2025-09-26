from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class QuestionQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        """Return questions visible to the user"""
        if not user or not user.is_authenticated:
            # Public approved questions only
            return self.filter(is_visible_publicly=True)

        # Own questions + public approved questions
        return self.filter(
            models.Q(owner=user) |
            models.Q(is_visible_publicly=True)
        )


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def visible_to_user(self, user):
        return self.get_queryset().visible_to_user(user)


class Question(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_DENIED = "DENIED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DENIED, "Denied"),
    ]

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    # user chooses, final visibility depends on status
    is_public = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    tags = models.ManyToManyField(Tag, blank=True, related_name="questions")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Postgres full-text search vector (title + body)
    search_vector = SearchVectorField(null=True, editable=False)

    objects = QuestionManager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
            models.Index(fields=["status", "is_public"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_visible_publicly(self):
        """Business rule: visible publicly only if approved and user set as public."""
        return self.is_public and self.status == self.STATUS_APPROVED


class QuestionVote(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="question_votes")
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="votes")
    rating = models.PositiveSmallIntegerField()  # 1..5
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "question")
        indexes = [models.Index(fields=["question", "rating"])]

    def clean(self):
        from django.core.exceptions import ValidationError
        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5")

    def __str__(self):
        return f"{self.user} -> {self.question} : {self.rating}"
