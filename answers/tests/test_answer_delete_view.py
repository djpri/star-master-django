import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from questions.models import Question
from answers.models import Answer, StarAnswer, BasicAnswer

User = get_user_model()


class AnswerDeleteViewTest(TestCase):
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

        # Create a private question for testing
        self.question = Question.objects.create(
            title="Test Question",
            body="Test question body",
            owner=self.user,
            is_public=False,
        )

        # Create a STAR answer
        self.star_answer = StarAnswer.objects.create(
            question=self.question,
            user=self.user,
            is_public=False,
            situation="Test situation",
            task="Test task",
            action="Test action",
            result="Test result",
        )

        # Create a Basic answer
        self.basic_answer = BasicAnswer.objects.create(
            question=self.question,
            user=self.user,
            is_public=False,
            text="This is a basic answer for testing.",
        )

        # Create an answer from another user
        self.other_answer = StarAnswer.objects.create(
            question=self.question,
            user=self.other_user,
            is_public=False,
            situation="Other situation",
            task="Other task",
            action="Other action",
            result="Other result",
        )

    def test_delete_answer_requires_login(self):
        """Anonymous users cannot delete answers"""
        url = reverse("answers:delete", kwargs={"pk": self.star_answer.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertTrue(Answer.objects.filter(pk=self.star_answer.pk).exists())

    def test_owner_can_delete_star_answer(self):
        """Answer owner can delete their own STAR answer"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("answers:delete", kwargs={"pk": self.star_answer.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("questions:detail", kwargs={"pk": self.question.pk}),
        )

        # Answer should be deleted
        self.assertFalse(
            Answer.objects.filter(pk=self.star_answer.pk).exists()
        )
        self.assertFalse(
            StarAnswer.objects.filter(pk=self.star_answer.pk).exists()
        )

        # Success message should be displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("STAR answer", str(messages[0]))
        self.assertIn("Test Question", str(messages[0]))
        self.assertIn("has been deleted", str(messages[0]))

    def test_owner_can_delete_basic_answer(self):
        """Answer owner can delete their own Basic answer"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("answers:delete", kwargs={"pk": self.basic_answer.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("questions:detail", kwargs={"pk": self.question.pk}),
        )

        # Answer should be deleted
        self.assertFalse(
            Answer.objects.filter(pk=self.basic_answer.pk).exists()
        )
        self.assertFalse(
            BasicAnswer.objects.filter(pk=self.basic_answer.pk).exists()
        )

        # Success message should mention Basic answer
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("BASIC answer", str(messages[0]))

    def test_non_owner_cannot_delete_answer(self):
        """Non-owners cannot delete answers"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("answers:delete", kwargs={"pk": self.other_answer.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Answer should still exist
        self.assertTrue(
            Answer.objects.filter(pk=self.other_answer.pk).exists()
        )

    def test_delete_only_accepts_post(self):
        """Delete view only accepts POST requests"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("answers:delete", kwargs={"pk": self.star_answer.pk})

        # GET request should not work
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

        # Answer should still exist
        self.assertTrue(Answer.objects.filter(pk=self.star_answer.pk).exists())

    def test_delete_nonexistent_answer(self):
        """Deleting a nonexistent answer returns 404"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("answers:delete", kwargs={"pk": 99999})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_redirects_to_question_detail(self):
        """After deletion, user is redirected to the question detail page"""
        self.client.login(username="testuser", password="testpass123")
        url = reverse("answers:delete", kwargs={"pk": self.star_answer.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("questions:detail", kwargs={"pk": self.question.pk}),
        )

    def test_delete_public_answer(self):
        """Can delete public answers owned by user"""
        # Make the answer public
        self.star_answer.is_public = True
        self.star_answer.save()

        self.client.login(username="testuser", password="testpass123")
        url = reverse("answers:delete", kwargs={"pk": self.star_answer.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Answer should be deleted
        self.assertFalse(
            Answer.objects.filter(pk=self.star_answer.pk).exists()
        )

        # Success message should be displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("STAR answer", str(messages[0]))

    def test_cascade_deletion_preserves_other_answers(self):
        """Deleting one answer doesn't affect other answers"""
        initial_answer_count = Answer.objects.count()

        self.client.login(username="testuser", password="testpass123")
        url = reverse("answers:delete", kwargs={"pk": self.star_answer.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # One answer should be deleted
        self.assertEqual(Answer.objects.count(), initial_answer_count - 1)

        # Other answers should still exist
        self.assertTrue(
            Answer.objects.filter(pk=self.basic_answer.pk).exists()
        )
        self.assertTrue(
            Answer.objects.filter(pk=self.other_answer.pk).exists()
        )
