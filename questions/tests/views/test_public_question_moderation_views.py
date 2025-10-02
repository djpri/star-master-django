import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from questions.models import Question

User = get_user_model()


@pytest.mark.django_db
class TestApprovePublicQuestionView:
    def test_admin_can_approve_pending_question(self, client):
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        owner = User.objects.create_user(
            username="owner", password="ownerpass123"
        )

        question = Question.objects.create(
            owner=owner,
            title="Pending leadership question",
            body="Tell me about a time you led a project.",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password="adminpass123")

        response = client.post(
            reverse("questions:approve_public", args=[question.pk]),
            HTTP_ACCEPT="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        question.refresh_from_db()
        assert question.status == Question.STATUS_APPROVED

    def test_non_admin_cannot_approve_pending_question(self, client):
        owner = User.objects.create_user(
            username="owner", password="ownerpass123"
        )
        other_user = User.objects.create_user(
            username="viewer", password="viewerpass123"
        )

        question = Question.objects.create(
            owner=owner,
            title="Pending behavioral question",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=other_user.username, password="viewerpass123")

        response = client.post(
            reverse("questions:approve_public", args=[question.pk]),
            HTTP_ACCEPT="application/json",
        )

        assert response.status_code == 403
        data = response.json()
        assert "error" in data

        question.refresh_from_db()
        assert question.status == Question.STATUS_PENDING

    def test_post_without_json_accept_redirects_to_public_list(self, client):
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        owner = User.objects.create_user(
            username="owner", password="ownerpass123"
        )

        question = Question.objects.create(
            owner=owner,
            title="Pending redirect question",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password="adminpass123")

        response = client.post(
            reverse("questions:approve_public", args=[question.pk]),
            data={"next": reverse("questions:public_list")},
        )

        assert response.status_code == 302
        assert response["Location"] == reverse("questions:public_list")

        question.refresh_from_db()
        assert question.status == Question.STATUS_APPROVED


@pytest.mark.django_db
class TestDenyPublicQuestionView:
    def test_admin_can_deny_pending_question(self, client):
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        owner = User.objects.create_user(
            username="owner", password="ownerpass123"
        )

        question = Question.objects.create(
            owner=owner,
            title="Pending denial question",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password="adminpass123")

        response = client.post(
            reverse("questions:deny_public", args=[question.pk]),
            HTTP_ACCEPT="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        question.refresh_from_db()
        assert question.status == Question.STATUS_DENIED

    def test_non_admin_cannot_deny_pending_question(self, client):
        owner = User.objects.create_user(
            username="owner", password="ownerpass123"
        )
        other_user = User.objects.create_user(
            username="viewer", password="viewerpass123"
        )

        question = Question.objects.create(
            owner=owner,
            title="Pending denial attempt",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=other_user.username, password="viewerpass123")

        response = client.post(
            reverse("questions:deny_public", args=[question.pk]),
            HTTP_ACCEPT="application/json",
        )

        assert response.status_code == 403
        data = response.json()
        assert "error" in data

        question.refresh_from_db()
        assert question.status == Question.STATUS_PENDING

    def test_html_request_redirects_after_denial(self, client):
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        owner = User.objects.create_user(
            username="owner", password="ownerpass123"
        )

        question = Question.objects.create(
            owner=owner,
            title="Redirect denial question",
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password="adminpass123")

        response = client.post(
            reverse("questions:deny_public", args=[question.pk]),
            data={"next": reverse("questions:public_list")},
        )

        assert response.status_code == 302
        assert response["Location"] == reverse("questions:public_list")

        question.refresh_from_db()
        assert question.status == Question.STATUS_DENIED
