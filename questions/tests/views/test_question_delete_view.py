import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from questions.models import Question
from answers.models import Answer, StarAnswer

User = get_user_model()


class QuestionDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )

        self.question = Question.objects.create(
            title="Test Question",
            body="Test question body",
            owner=self.user,
            is_public=False,
        )
        self.other_question = Question.objects.create(
            title="Other User Question",
            body="Other question body",
            owner=self.other_user,
            is_public=False,
        )

    def test_delete_question_requires_login(self):
        """Anonymous users cannot delete questions"""
        url = reverse("questions:delete", kwargs={"pk": self.question.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())

    def test_owner_can_delete_question(self):
        """Question owner can delete their own question"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("questions:delete", kwargs={"pk": self.question.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("questions:list"))

        # Question should be deleted
        self.assertFalse(Question.objects.filter(pk=self.question.pk).exists())

        # Success message should be displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Test Question", str(messages[0]))
        self.assertIn("has been deleted", str(messages[0]))

    def test_non_owner_cannot_delete_question(self):
        """Non-owners cannot delete questions"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse(
            "questions:delete", kwargs={"pk": self.other_question.pk}
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Question should still exist
        self.assertTrue(
            Question.objects.filter(pk=self.other_question.pk).exists()
        )

    def test_delete_question_with_answers(self):
        """Deleting a question also deletes associated answers"""
        # Create a STAR answer for the question
        star_answer = StarAnswer.objects.create(
            question=self.question,
            user=self.user,
            is_public=False,
            situation="Test situation",
            task="Test task",
            action="Test action",
            result="Test result",
        )

        self.client.login(username="testuser", password="testpass123")
        url = reverse("questions:delete", kwargs={"pk": self.question.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Question and answers should be deleted (cascade)
        self.assertFalse(Question.objects.filter(pk=self.question.pk).exists())
        self.assertFalse(StarAnswer.objects.filter(pk=star_answer.pk).exists())

        # Success message should mention the answer count
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("1 answer", str(messages[0]))

    def test_delete_only_accepts_post(self):
        """Delete view only accepts POST requests"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("questions:delete", kwargs={"pk": self.question.pk})

        # GET request should not work
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

        # Question should still exist
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())

    def test_delete_nonexistent_question(self):
        """Deleting a nonexistent question returns 404"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("questions:delete", kwargs={"pk": 99999})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_public_question_with_community_answers(self):
        """Deleting a public question with community answers works correctly"""
        # Make question public and approved
        self.question.is_public = True
        self.question.status = Question.STATUS_APPROVED
        self.question.save()

        # Create a community answer from another user
        community_answer = StarAnswer.objects.create(
            question=self.question,
            user=self.other_user,
            is_public=True,
            situation="Community situation",
            task="Community task",
            action="Community action",
            result="Community result",
        )

        self.client.login(username="testuser", password="testpass123")
        url = reverse("questions:delete", kwargs={"pk": self.question.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Question and all associated answers should be deleted
        self.assertFalse(Question.objects.filter(pk=self.question.pk).exists())
        self.assertFalse(
            Answer.objects.filter(question_id=self.question.pk).exists()
        )
