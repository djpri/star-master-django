"""
Tests for visibility filtering on private question list page.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from questions.models import Question

User = get_user_model()


@pytest.mark.django_db
class TestQuestionListVisibilityFilter:
    """Test visibility filtering on the private question list page."""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    @pytest.fixture
    def questions(self, user):
        """Create test questions - both private and public."""
        private1 = Question.objects.create(
            owner=user,
            title="Private Question 1",
            body="Personal question",
            is_public=False,
        )
        private2 = Question.objects.create(
            owner=user,
            title="Private Question 2",
            body="Another personal question",
            is_public=False,
        )
        public1 = Question.objects.create(
            owner=user,
            title="Public Question 1",
            body="Public question pending",
            is_public=True,
            status=Question.STATUS_PENDING,
        )
        public2 = Question.objects.create(
            owner=user,
            title="Public Question 2",
            body="Public question approved",
            is_public=True,
            status=Question.STATUS_APPROVED,
        )
        return {
            "private": [private1, private2],
            "public": [public1, public2],
        }

    def test_default_shows_only_personal_questions(
        self, client, user, questions
    ):
        """Test default view shows only personal (private) questions."""
        client.force_login(user)
        response = client.get(reverse("questions:list"))

        assert response.status_code == 200
        questions_list = list(response.context["questions"])

        # Should show both private questions
        assert len(questions_list) == 2
        assert questions["private"][0] in questions_list
        assert questions["private"][1] in questions_list

        # Should not show public questions
        assert questions["public"][0] not in questions_list
        assert questions["public"][1] not in questions_list

        # Check context
        assert response.context["selected_view"] == "personal"

    def test_view_public_shows_only_public_questions(
        self, client, user, questions
    ):
        """Test 'public' view shows only public questions."""
        client.force_login(user)
        response = client.get(
            reverse("questions:list"), {"view": "public"}
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])

        # Should show both public questions (pending and approved)
        assert len(questions_list) == 2
        assert questions["public"][0] in questions_list
        assert questions["public"][1] in questions_list

        # Should not show private questions
        assert questions["private"][0] not in questions_list
        assert questions["private"][1] not in questions_list

        # Check context
        assert response.context["selected_view"] == "public"

    def test_view_all_shows_all_questions(self, client, user, questions):
        """Test 'all' view shows both private and public questions."""
        client.force_login(user)
        response = client.get(reverse("questions:list"), {"view": "all"})

        assert response.status_code == 200
        questions_list = list(response.context["questions"])

        # Should show all 4 questions
        assert len(questions_list) == 4
        assert questions["private"][0] in questions_list
        assert questions["private"][1] in questions_list
        assert questions["public"][0] in questions_list
        assert questions["public"][1] in questions_list

        # Check context
        assert response.context["selected_view"] == "all"

    def test_invalid_view_defaults_to_personal(
        self, client, user, questions
    ):
        """Test invalid view parameter defaults to personal."""
        client.force_login(user)
        response = client.get(
            reverse("questions:list"), {"view": "invalid"}
        )

        assert response.status_code == 200
        assert response.context["selected_view"] == "personal"
        questions_list = list(response.context["questions"])
        # Should show only private questions
        assert len(questions_list) == 2

    def test_view_options_in_context(self, client, user):
        """Test view options are available in context."""
        client.force_login(user)
        response = client.get(reverse("questions:list"))

        assert response.status_code == 200
        assert "view_options" in response.context
        assert "selected_view" in response.context
        assert "selected_view_label" in response.context

        # Check options structure
        view_options = response.context["view_options"]
        assert len(view_options) == 3
        assert ("personal", "Personal Questions Only") in view_options
        assert ("public", "Your Public Questions") in view_options
        assert ("all", "All Your Questions") in view_options

    def test_view_preserves_sort(self, client, user, questions):
        """Test view filter preserves sort parameter."""
        client.force_login(user)
        response = client.get(
            reverse("questions:list"),
            {"view": "public", "sort": "title"},
        )

        assert response.status_code == 200
        assert response.context["selected_view"] == "public"
        assert response.context["selected_sort"] == "title"

        questions_list = list(response.context["questions"])
        # Check sorting is applied (alphabetical)
        assert questions_list[0].title < questions_list[1].title

    def test_view_preserves_tag_filter(self, client, user, questions):
        """Test view filter works with tag filtering."""
        from questions.models import Tag

        tag = Tag.objects.create(
            name="TestTag", slug="testtag", is_public=True
        )
        questions["private"][0].tags.add(tag)

        client.force_login(user)
        response = client.get(
            reverse("questions:list"),
            {"view": "personal", "tag": "testtag"},
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])

        # Should show only the private question with the tag
        assert len(questions_list) == 1
        assert questions_list[0].id == questions["private"][0].id

    def test_view_preserves_search(self, client, user, questions):
        """Test view filter works with search."""
        client.force_login(user)
        response = client.get(
            reverse("questions:list"),
            {"view": "personal", "search": "Private Question 1"},
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])

        # Should find the searched private question
        assert len(questions_list) == 1
        assert questions_list[0].id == questions["private"][0].id

    def test_unauthenticated_redirects(self, client):
        """Test unauthenticated users are redirected."""
        response = client.get(
            reverse("questions:list"), {"view": "public"}
        )

        assert response.status_code == 302
        assert "public" in response.url

    def test_empty_results_for_view_mode(self, client, user):
        """Test empty results when no questions match view mode."""
        # Create only private questions
        Question.objects.create(
            owner=user,
            title="Private Only",
            body="Test",
            is_public=False,
        )

        client.force_login(user)
        response = client.get(
            reverse("questions:list"), {"view": "public"}
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        assert len(questions_list) == 0
