import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from questions.models import Question

User = get_user_model()


@pytest.mark.django_db
class TestPublicQuestionListView:
    def test_admin_sees_pending_section_when_pending_questions_exist(self, client):
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        Question.objects.create(
            owner=admin_user,
            title="Pending community question",
            body="Describe a situation where you led a team.",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password="adminpass123")

        response = client.get(reverse("questions:public_list"))

        assert response.status_code == 200
        assert "Pending Questions" in response.content.decode()
