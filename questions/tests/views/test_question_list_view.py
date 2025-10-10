import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from questions.models import Question

User = get_user_model()


@pytest.mark.django_db
class TestQuestionListViewBadges:
    def test_private_question_shows_private_badge(self, client):
        user = User.objects.create_user(
            username="private_user", password="testpass123"
        )
        Question.objects.create(
            owner=user,
            title="Describe a time you led a team",
            is_public=False,
            status=Question.STATUS_APPROVED,
        )

        client.login(username=user.username, password="testpass123")
        response = client.get(reverse("questions:list"))

        content = response.content.decode()
        assert "Private" in content
        assert 'data-testid="public-badge"' not in content

    def test_pending_public_question_shows_request_and_pending_badges(
        self, client
    ):
        user = User.objects.create_user(
            username="pending_user", password="testpass123"
        )
        Question.objects.create(
            owner=user,
            title="Tell me about handling conflicting priorities",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=user.username, password="testpass123")
        # Need to view public questions to see public question badges
        response = client.get(reverse("questions:list"), {"view": "public"})

        content = response.content.decode()
        assert 'data-testid="public-badge"' in content
        assert "Public" in content
        assert "Pending review" in content

    def test_denied_public_question_shows_denied_badge(self, client):
        user = User.objects.create_user(
            username="denied_user", password="testpass123"
        )
        Question.objects.create(
            owner=user,
            title="Describe a challenging stakeholder",
            is_public=True,
            status=Question.STATUS_DENIED,
        )

        client.login(username=user.username, password="testpass123")
        # Need to view public questions to see public question badges
        response = client.get(reverse("questions:list"), {"view": "public"})

        content = response.content.decode()
        assert 'data-testid="public-badge"' in content
        assert "Public" in content
        assert "Request denied" in content
