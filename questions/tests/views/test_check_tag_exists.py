import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from questions.models import Tag

User = get_user_model()


@pytest.mark.django_db
class TestCheckTagExistsView:
    """Test the AJAX endpoint for checking if tags exist."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    @pytest.fixture
    def other_user(self):
        """Create another test user."""
        return User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )

    @pytest.fixture
    def public_tag(self):
        """Create a public tag."""
        return Tag.objects.create(
            name="Leadership",
            slug="leadership",
            is_public=True,
            owner=None,
        )

    @pytest.fixture
    def personal_tag(self, user):
        """Create a personal tag for the test user."""
        return Tag.objects.create(
            name="MyPersonalTag",
            slug="mypersonaltag",
            is_public=False,
            owner=user,
        )

    def test_check_tag_exists_requires_login(self):
        """Test that the endpoint requires authentication."""
        client = Client()
        url = reverse("questions:check_tag_exists")

        response = client.get(url, {"name": "TestTag"})

        # Should redirect to login page
        assert response.status_code == 302

    def test_check_tag_exists_only_allows_get(self, user):
        """Test that only GET requests are allowed."""
        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.post(url, {"name": "TestTag"})

        assert response.status_code == 405
        data = response.json()
        assert data["error"] == "Only GET method allowed"

    def test_check_tag_exists_requires_name_parameter(self, user):
        """Test that tag name parameter is required."""
        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.get(url)

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Tag name is required"

    def test_check_tag_exists_finds_public_tag(self, user, public_tag):
        """Test that existing public tags are found."""
        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.get(url, {"name": "Leadership"})

        assert response.status_code == 200
        data = response.json()
        assert data["exists"] is True
        assert data["tag"]["id"] == public_tag.pk
        assert data["tag"]["name"] == "Leadership"
        assert data["tag"]["is_public"] is True
        assert data["tag"]["can_use"] is True

    def test_check_tag_exists_finds_personal_tag(self, user, personal_tag):
        """Test that user's personal tags are found."""
        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.get(url, {"name": "MyPersonalTag"})

        assert response.status_code == 200
        data = response.json()
        assert data["exists"] is True
        assert data["tag"]["id"] == personal_tag.pk
        assert data["tag"]["name"] == "MyPersonalTag"
        assert data["tag"]["is_public"] is False
        assert data["tag"]["can_use"] is True

    def test_check_tag_exists_case_insensitive(self, user, public_tag):
        """Test that tag checking is case-insensitive."""
        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.get(url, {"name": "leadership"})  # lowercase

        assert response.status_code == 200
        data = response.json()
        assert data["exists"] is True
        assert data["tag"]["id"] == public_tag.pk
        assert data["tag"]["name"] == "Leadership"

    def test_check_tag_exists_does_not_find_other_users_personal_tags(
        self, user, other_user
    ):
        """Test that users cannot see other users' personal tags."""
        # Create a personal tag for other_user
        other_tag = Tag.objects.create(
            name="OtherUserTag",
            slug="otherusertag",
            is_public=False,
            owner=other_user,
        )

        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.get(url, {"name": "OtherUserTag"})

        assert response.status_code == 200
        data = response.json()
        assert data["exists"] is False
        assert data["can_create"] is True

    def test_check_tag_exists_prefers_public_over_personal(
        self, user, public_tag
    ):
        """
        Test that public tags are preferred over personal tags
        with same name.
        """
        # Create a personal tag with the same name
        personal_tag_same_name = Tag.objects.create(
            name="Leadership",
            slug="leadership-personal",
            is_public=False,
            owner=user,
        )

        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.get(url, {"name": "Leadership"})

        assert response.status_code == 200
        data = response.json()
        assert data["exists"] is True
        # Should return public tag, not personal
        assert data["tag"]["id"] == public_tag.pk
        assert data["tag"]["is_public"] is True

    def test_check_tag_exists_returns_can_create_for_new_tag(self, user):
        """Test that non-existing tags return can_create=True."""
        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.get(url, {"name": "CompletelyNewTag"})

        assert response.status_code == 200
        data = response.json()
        assert data["exists"] is False
        assert data["can_create"] is True

    def test_check_tag_exists_handles_empty_name(self, user):
        """Test that empty tag names are handled properly."""
        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.get(url, {"name": "   "})  # whitespace only

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Tag name is required"

    def test_check_tag_exists_trims_whitespace(self, user, public_tag):
        """Test that tag names are trimmed of whitespace."""
        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("questions:check_tag_exists")

        response = client.get(
            url, {"name": "  Leadership  "}
        )  # with whitespace

        assert response.status_code == 200
        data = response.json()
        assert data["exists"] is True
        assert data["tag"]["id"] == public_tag.pk
        assert data["tag"]["name"] == "Leadership"
