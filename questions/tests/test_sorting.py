"""
Tests for sorting functionality on question list pages.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from questions.models import Question, Tag
from answers.models import BasicAnswer

User = get_user_model()


@pytest.mark.django_db
class TestPublicQuestionListSorting:
    """Test sorting on the public question list page."""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    @pytest.fixture
    def questions(self, user):
        """Create test public questions with different dates/titles."""
        q1 = Question.objects.create(
            owner=user,
            title="Alpha Question",
            body="First alphabetically",
            is_public=True,
            status=Question.STATUS_APPROVED,
        )
        q2 = Question.objects.create(
            owner=user,
            title="Zeta Question",
            body="Last alphabetically",
            is_public=True,
            status=Question.STATUS_APPROVED,
        )
        q3 = Question.objects.create(
            owner=user,
            title="Beta Question",
            body="Middle alphabetically",
            is_public=True,
            status=Question.STATUS_APPROVED,
        )
        # Set different creation times
        q1.created_at = "2024-01-01T00:00:00Z"
        q2.created_at = "2024-01-03T00:00:00Z"
        q3.created_at = "2024-01-02T00:00:00Z"
        q1.save()
        q2.save()
        q3.save()
        return [q1, q2, q3]

    def test_default_sort_newest_first(self, client, questions):
        """Test default sorting is newest first."""
        response = client.get(reverse("questions:public_list"))

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        # Newest to oldest: q2, q3, q1
        assert questions_list[0].id == questions[1].id
        assert questions_list[1].id == questions[2].id
        assert questions_list[2].id == questions[0].id

    def test_sort_by_oldest_first(self, client, questions):
        """Test sorting by oldest first."""
        response = client.get(
            reverse("questions:public_list"), {"sort": "created_at"}
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        # Oldest to newest: q1, q3, q2
        assert questions_list[0].id == questions[0].id
        assert questions_list[1].id == questions[2].id
        assert questions_list[2].id == questions[1].id

    def test_sort_by_title_asc(self, client, questions):
        """Test sorting by title A-Z."""
        response = client.get(
            reverse("questions:public_list"), {"sort": "title"}
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        # Alpha, Beta, Zeta
        assert questions_list[0].id == questions[0].id
        assert questions_list[1].id == questions[2].id
        assert questions_list[2].id == questions[1].id

    def test_sort_by_title_desc(self, client, questions):
        """Test sorting by title Z-A."""
        response = client.get(
            reverse("questions:public_list"), {"sort": "-title"}
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        # Zeta, Beta, Alpha
        assert questions_list[0].id == questions[1].id
        assert questions_list[1].id == questions[2].id
        assert questions_list[2].id == questions[0].id

    def test_invalid_sort_defaults_to_newest(self, client, questions):
        """Test invalid sort parameter defaults to newest first."""
        response = client.get(
            reverse("questions:public_list"), {"sort": "invalid"}
        )

        assert response.status_code == 200
        assert response.context["selected_sort"] == "-created_at"
        questions_list = list(response.context["questions"])
        # Should default to newest first
        assert questions_list[0].id == questions[1].id

    def test_sort_label_in_context(self, client, questions):
        """Test sort label is correctly set in context."""
        response = client.get(
            reverse("questions:public_list"), {"sort": "title"}
        )

        assert response.status_code == 200
        assert response.context["selected_sort_label"] == "Title (A-Z)"

    def test_sort_with_tag_filter(self, client, user, questions):
        """Test sorting works with tag filtering."""
        tag = Tag.objects.create(
            name="TestTag", slug="testtag", is_public=True
        )
        questions[0].tags.add(tag)
        questions[1].tags.add(tag)

        response = client.get(
            reverse("questions:public_list"),
            {"tag": "testtag", "sort": "title"},
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        assert len(questions_list) == 2
        # Alpha before Zeta
        assert questions_list[0].id == questions[0].id
        assert questions_list[1].id == questions[1].id


@pytest.mark.django_db
class TestPrivateQuestionListSorting:
    """Test sorting on the private question list page."""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    @pytest.fixture
    def questions_with_answers(self, user):
        """Create test private questions with different answer counts."""
        q1 = Question.objects.create(
            owner=user,
            title="Alpha Question",
            body="Question one",
        )
        q2 = Question.objects.create(
            owner=user,
            title="Zeta Question",
            body="Question two",
        )
        q3 = Question.objects.create(
            owner=user,
            title="Beta Question",
            body="Question three",
        )
        # Set different creation times
        q1.created_at = "2024-01-01T00:00:00Z"
        q2.created_at = "2024-01-03T00:00:00Z"
        q3.created_at = "2024-01-02T00:00:00Z"
        q1.save()
        q2.save()
        q3.save()

        # Add different number of answers
        BasicAnswer.objects.create(
            question=q1, user=user, text="Answer 1 for q1"
        )
        BasicAnswer.objects.create(
            question=q1, user=user, text="Answer 2 for q1"
        )
        BasicAnswer.objects.create(
            question=q1, user=user, text="Answer 3 for q1"
        )
        BasicAnswer.objects.create(
            question=q2, user=user, text="Answer 1 for q2"
        )
        # q3 has no answers

        return [q1, q2, q3]

    def test_sort_by_most_answers(self, client, user, questions_with_answers):
        """Test sorting by most answers first."""
        client.force_login(user)
        response = client.get(
            reverse("questions:list"), {"sort": "-answer_count"}
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        # q1 (3), q2 (1), q3 (0)
        assert questions_list[0].id == questions_with_answers[0].id
        assert questions_list[1].id == questions_with_answers[1].id
        assert questions_list[2].id == questions_with_answers[2].id
        # Verify counts are correct
        assert questions_list[0].answer_count == 3
        assert questions_list[1].answer_count == 1
        assert questions_list[2].answer_count == 0

    def test_sort_by_fewest_answers(
        self, client, user, questions_with_answers
    ):
        """Test sorting by fewest answers first."""
        client.force_login(user)
        response = client.get(
            reverse("questions:list"), {"sort": "answer_count"}
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        # q3 (0), q2 (1), q1 (3)
        assert questions_list[0].id == questions_with_answers[2].id
        assert questions_list[1].id == questions_with_answers[1].id
        assert questions_list[2].id == questions_with_answers[0].id

    def test_sort_by_title_with_answers(
        self, client, user, questions_with_answers
    ):
        """Test sorting by title when answers exist."""
        client.force_login(user)
        response = client.get(reverse("questions:list"), {"sort": "title"})

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        # Alpha, Beta, Zeta
        assert questions_list[0].id == questions_with_answers[0].id
        assert questions_list[1].id == questions_with_answers[2].id
        assert questions_list[2].id == questions_with_answers[1].id
        # Answer counts should still be attached
        assert hasattr(questions_list[0], "answer_count")
        assert questions_list[0].answer_count == 3

    def test_sort_preserves_filter(self, client, user, questions_with_answers):
        """Test sorting preserves tag filter."""
        tag = Tag.objects.create(
            name="TestTag", slug="testtag", is_public=True
        )
        questions_with_answers[0].tags.add(tag)

        client.force_login(user)
        response = client.get(
            reverse("questions:list"),
            {"tag": "testtag", "sort": "-answer_count"},
        )

        assert response.status_code == 200
        questions_list = list(response.context["questions"])
        assert len(questions_list) == 1
        assert questions_list[0].id == questions_with_answers[0].id
        assert questions_list[0].answer_count == 3

    def test_unauthenticated_redirects(self, client):
        """Test unauthenticated users are redirected."""
        response = client.get(
            reverse("questions:list"), {"sort": "title"}
        )
        assert response.status_code == 302
        assert "public" in response.url


@pytest.mark.django_db
class TestSortingPerformance:
    """Test that sorting maintains good performance."""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_answer_count_sort_uses_annotation(
        self, client, user, django_assert_num_queries
    ):
        """Test answer count sorting uses efficient annotation."""
        # Create questions with answers
        for i in range(5):
            q = Question.objects.create(
                owner=user,
                title=f"Question {i}",
                body="Body",
            )
            for j in range(i):
                BasicAnswer.objects.create(
                    question=q, user=user, text=f"Answer {j}"
                )

        client.force_login(user)
        # Should be efficient with annotation - no separate answer count
        # query needed
        with django_assert_num_queries(6):
            response = client.get(
                reverse("questions:list"), {"sort": "-answer_count"}
            )
            assert response.status_code == 200
            # Force evaluation
            list(response.context["questions"])

    def test_title_sort_does_not_query_answers(
        self, client, user, django_assert_num_queries
    ):
        """Test title sorting doesn't query answers unnecessarily."""
        # Create questions
        for i in range(5):
            Question.objects.create(
                owner=user,
                title=f"Question {i}",
                body="Body",
            )

        client.force_login(user)
        # Title sorting should not need answer queries except for count
        # display
        with django_assert_num_queries(7):
            response = client.get(
                reverse("questions:list"), {"sort": "title"}
            )
            assert response.status_code == 200
            # Force evaluation
            list(response.context["questions"])
