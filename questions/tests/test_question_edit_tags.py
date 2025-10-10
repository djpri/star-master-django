"""
Test to verify that tags are properly saved when editing a question.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from questions.models import Question, Tag


class TestQuestionEditTags(TestCase):
    """Test that tags can be added to existing questions via the edit form."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Create a private question without tags
        self.question = Question.objects.create(
            title="Test Question",
            body="Test body",
            owner=self.user,
            is_public=False,
            status=Question.STATUS_PENDING,
        )

        # Create a public tag
        self.public_tag = Tag.objects.create(
            name="public-tag", is_public=True, owner=None
        )

    def test_add_tags_to_existing_question(self):
        """Test that tags can be added when editing an existing question."""
        self.client.login(username="testuser", password="testpass123")

        # Verify question has no tags initially
        self.assertEqual(self.question.tags.count(), 0)

        url = reverse("questions:edit", kwargs={"pk": self.question.pk})

        # Submit edit form with tags
        form_data = {
            "title": self.question.title,
            "body": self.question.body,
            "is_public": False,
            "tags_input": "public-tag,new-tag",
        }

        response = self.client.post(url, form_data)

        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)

        # Refresh question from database
        self.question.refresh_from_db()

        # Verify tags were added
        self.assertEqual(self.question.tags.count(), 2)
        tag_names = set(self.question.tags.values_list("name", flat=True))
        self.assertIn("public-tag", tag_names)
        self.assertIn("new-tag", tag_names)

    def test_update_tags_on_existing_question(self):
        """Test that existing tags can be replaced when editing."""
        # Add initial tag
        initial_tag = Tag.objects.create(
            name="initial-tag", owner=self.user, is_public=False
        )
        self.question.tags.add(initial_tag)

        self.client.login(username="testuser", password="testpass123")

        # Verify question has one tag
        self.assertEqual(self.question.tags.count(), 1)

        url = reverse("questions:edit", kwargs={"pk": self.question.pk})

        # Submit edit form with different tags
        form_data = {
            "title": self.question.title,
            "body": self.question.body,
            "is_public": False,
            "tags_input": "updated-tag,another-tag",
        }

        response = self.client.post(url, form_data)

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Refresh question
        self.question.refresh_from_db()

        # Verify tags were replaced
        self.assertEqual(self.question.tags.count(), 2)
        tag_names = set(self.question.tags.values_list("name", flat=True))
        self.assertNotIn("initial-tag", tag_names)
        self.assertIn("updated-tag", tag_names)
        self.assertIn("another-tag", tag_names)
