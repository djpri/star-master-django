import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from questions.models import Question

User = get_user_model()


@pytest.mark.django_db
class TestQuestionCreateView:
    """Test the question_create view and query parameter handling."""

    def test_create_view_sets_is_public_true_with_query_param(self, client):
        user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        response = client.get(reverse("questions:create") + "?public=true")

        assert response.status_code == 200
        assert response.context["form"].initial.get("is_public") is True
        assert response.context["is_public_question"] is True

    def test_create_view_sets_is_public_false_with_query_param(self, client):
        user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        response = client.get(reverse("questions:create") + "?public=false")

        assert response.status_code == 200
        assert response.context["form"].initial.get("is_public") is False
        assert response.context["is_public_question"] is False

    def test_create_view_without_query_param(self, client):
        user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        response = client.get(reverse("questions:create"))

        assert response.status_code == 200
        assert "is_public" not in response.context["form"].initial
        assert response.context["is_public_question"] is False

    def test_create_view_with_invalid_query_param(self, client):
        user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        response = client.get(reverse("questions:create") + "?public=invalid")

        assert response.status_code == 200
        assert "is_public" not in response.context["form"].initial
        assert response.context["is_public_question"] is False

    def test_regular_user_submitting_public_question_saves_as_pending(
        self, client
    ):
        user = User.objects.create_user(
            username="creator", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        response = client.post(
            reverse("questions:create") + "?public=true",
            data={
                "title": "Describe a time you influenced stakeholders",
                "body": "",
            },
        )

        assert response.status_code == 302
        question = Question.objects.get(owner=user)
        assert question.is_public is True
        assert question.status == Question.STATUS_PENDING

    def test_pending_public_question_shown_only_to_admin_in_public_list(
        self, client
    ):
        user = User.objects.create_user(
            username="creator", password="testpass123"
        )
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

        client.login(username=user.username, password="testpass123")
        client.post(
            reverse("questions:create") + "?public=true",
            data={
                "title": "Tell me about handling a difficult stakeholder",
                "body": "",
            },
        )
        question = Question.objects.get(owner=user)
        client.logout()

        # Anonymous/public view should not include pending question
        response = client.get(reverse("questions:public_list"))
        assert response.status_code == 200
        public_titles = {q.title for q in response.context["questions"]}
        assert question.title not in public_titles

        # Admin sees pending question in moderation queue
        client.login(username=admin.username, password="adminpass123")
        response = client.get(reverse("questions:public_list"))
        assert response.status_code == 200
        pending_titles = {
            q.title for q in response.context["pending_questions"]
        }
        assert question.title in pending_titles
