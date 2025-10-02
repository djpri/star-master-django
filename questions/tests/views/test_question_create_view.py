import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

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
