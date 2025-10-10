"""
Test that available tags are filtered correctly based on question visibility.

For public questions: only public tags should be available
For private questions: both public tags and user's personal tags should be
available
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from questions.models import Question, Tag

User = get_user_model()


@pytest.mark.django_db
class TestAvailableTagsInQuestionCreate:
    """Test that available tags are filtered correctly in question create."""

    def test_public_question_shows_only_public_tags(self, client):
        """
        When creating a public question, only public tags should be in
        available_tags.
        """
        user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        # Create public and private tags
        public_tag = Tag.objects.create(
            name="public-tag", is_public=True, owner=None
        )
        private_tag = Tag.objects.create(
            name="private-tag", is_public=False, owner=user
        )

        response = client.get(reverse("questions:create") + "?public=true")

        assert response.status_code == 200
        available_tags = response.context["available_tags"]

        # Should only include public tags
        assert public_tag in available_tags
        assert private_tag not in available_tags

    def test_private_question_shows_public_and_user_tags(self, client):
        """
        When creating a private question, both public tags and user's personal
        tags should be available.
        """
        user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        # Create tags with different ownership
        public_tag = Tag.objects.create(
            name="public-tag", is_public=True, owner=None
        )
        user_private_tag = Tag.objects.create(
            name="my-private-tag", is_public=False, owner=user
        )
        other_user_private_tag = Tag.objects.create(
            name="other-private-tag", is_public=False, owner=other_user
        )

        response = client.get(
            reverse("questions:create") + "?public=false"
        )

        assert response.status_code == 200
        available_tags = response.context["available_tags"]

        # Should include public tags and user's own private tags
        assert public_tag in available_tags
        assert user_private_tag in available_tags
        # Should NOT include other user's private tags
        assert other_user_private_tag not in available_tags

    def test_default_create_shows_public_and_user_tags(self, client):
        """
        When creating a question without specifying public/private, it
        defaults to private, so should show public and user tags.
        """
        user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        public_tag = Tag.objects.create(
            name="public-tag", is_public=True, owner=None
        )
        user_private_tag = Tag.objects.create(
            name="my-private-tag", is_public=False, owner=user
        )

        response = client.get(reverse("questions:create"))

        assert response.status_code == 200
        available_tags = response.context["available_tags"]

        # Defaults to private, so should show both
        assert public_tag in available_tags
        assert user_private_tag in available_tags


@pytest.mark.django_db
class TestAvailableTagsInQuestionEdit:
    """Test that available tags are filtered correctly in question edit."""

    def test_editing_public_question_shows_only_public_tags(self, client):
        """
        When editing a public question, only public tags should be in
        available_tags.
        """
        user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        # Create a public question
        question = Question.objects.create(
            title="Public Question",
            body="Test body",
            owner=user,
            is_public=True,
            status=Question.STATUS_APPROVED,
        )

        # Create public and private tags
        public_tag = Tag.objects.create(
            name="public-tag", is_public=True, owner=None
        )
        private_tag = Tag.objects.create(
            name="private-tag", is_public=False, owner=user
        )

        response = client.get(
            reverse("questions:edit", kwargs={"pk": question.pk})
        )

        assert response.status_code == 200
        available_tags = response.context["available_tags"]

        # Should only include public tags
        assert public_tag in available_tags
        assert private_tag not in available_tags

    def test_editing_private_question_shows_public_and_user_tags(
        self, client
    ):
        """
        When editing a private question, both public tags and user's personal
        tags should be available.
        """
        user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        client.login(username=user.username, password="testpass123")

        # Create a private question
        question = Question.objects.create(
            title="Private Question",
            body="Test body",
            owner=user,
            is_public=False,
            status=Question.STATUS_APPROVED,
        )

        # Create tags with different ownership
        public_tag = Tag.objects.create(
            name="public-tag", is_public=True, owner=None
        )
        user_private_tag = Tag.objects.create(
            name="my-private-tag", is_public=False, owner=user
        )
        other_user_private_tag = Tag.objects.create(
            name="other-private-tag", is_public=False, owner=other_user
        )

        response = client.get(
            reverse("questions:edit", kwargs={"pk": question.pk})
        )

        assert response.status_code == 200
        available_tags = response.context["available_tags"]

        # Should include public tags and user's own private tags
        assert public_tag in available_tags
        assert user_private_tag in available_tags
        # Should NOT include other user's private tags
        assert other_user_private_tag not in available_tags

    def test_admin_editing_public_question_shows_only_public_tags(
        self, client
    ):
        """
        When an admin edits a public question, only public tags should be
        available.
        """
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        client.login(username=admin.username, password="adminpass123")

        # Create a public question owned by another user
        question = Question.objects.create(
            title="Public Question",
            body="Test body",
            owner=other_user,
            is_public=True,
            status=Question.STATUS_APPROVED,
        )

        # Create public and admin's private tags
        public_tag = Tag.objects.create(
            name="public-tag", is_public=True, owner=None
        )
        admin_private_tag = Tag.objects.create(
            name="admin-private-tag", is_public=False, owner=admin
        )

        response = client.get(
            reverse("questions:edit", kwargs={"pk": question.pk})
        )

        assert response.status_code == 200
        available_tags = response.context["available_tags"]

        # Should only include public tags, not admin's private tags
        assert public_tag in available_tags
        assert admin_private_tag not in available_tags

    def test_admin_editing_private_question_shows_public_and_admin_tags(
        self, client
    ):
        """
        When an admin edits their own private question, both public tags and
        admin's personal tags should be available.
        """
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        client.login(username=admin.username, password="adminpass123")

        # Create admin's private question
        question = Question.objects.create(
            title="Admin Private Question",
            body="Test body",
            owner=admin,
            is_public=False,
            status=Question.STATUS_APPROVED,
        )

        # Create public and admin's private tags
        public_tag = Tag.objects.create(
            name="public-tag", is_public=True, owner=None
        )
        admin_private_tag = Tag.objects.create(
            name="admin-private-tag", is_public=False, owner=admin
        )

        response = client.get(
            reverse("questions:edit", kwargs={"pk": question.pk})
        )

        assert response.status_code == 200
        available_tags = response.context["available_tags"]

        # Should include both public and admin's private tags
        assert public_tag in available_tags
        assert admin_private_tag in available_tags
