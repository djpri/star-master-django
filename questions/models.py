from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60)
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tags", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        # Ensure unique combinations - public tags have no owner (NULL), personal tags are unique per owner
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'owner'],
                name='unique_tag_per_user'
            ),
            models.UniqueConstraint(
                fields=['name'],
                condition=models.Q(is_public=True),
                name='unique_public_tag'
            )
        ]
        ordering = ['name']

    def __str__(self):
        if self.is_public:
            return f"{self.name} (public)"
        return f"{self.name} ({self.owner.username if self.owner else 'no owner'})"


class QuestionQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        """Return all questions visible to the user (used for answers context)"""
        if not user or not user.is_authenticated:
            # Public approved questions only
            return self.filter(is_public=True, status="APPROVED")

        # Own questions (both private and public) + public approved questions from others
        return self.filter(
            models.Q(owner=user) |
            models.Q(is_public=True, status="APPROVED")
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
