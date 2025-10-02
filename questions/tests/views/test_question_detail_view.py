import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from questions.models import Question

User = get_user_model()


@pytest.mark.django_db
class TestQuestionDetailView:
    def test_admin_can_view_pending_public_question(self, client):
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        owner = User.objects.create_user(
            username="owner", password="ownerpass123"
        )

        question = Question.objects.create(
            owner=owner,
            title="Pending situation question",
            body="Describe a situation you handled pending approval.",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password="adminpass123")

        response = client.get(reverse("questions:detail", args=[question.pk]))

        assert response.status_code == 200
        content = response.content.decode()
        assert "Approve Question" in content
        assert "Deny Question" in content
        assert "Community Question Template" not in content

    def test_non_admin_gets_404_for_pending_public_question(self, client):
        owner = User.objects.create_user(
            username="owner", password="ownerpass123"
        )
        other_user = User.objects.create_user(
            username="viewer", password="viewerpass123"
        )

        question = Question.objects.create(
            owner=owner,
            title="Pending task question",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=other_user.username, password="viewerpass123")

        response = client.get(reverse("questions:detail", args=[question.pk]))

        assert response.status_code == 404

    def test_question_not_found_returns_404(self, client):
        user = User.objects.create_user(
            username="viewer", password="viewerpass123"
        )

        client.login(username=user.username, password="viewerpass123")

        response = client.get(reverse("questions:detail", args=[9999]))

        assert response.status_code == 404
