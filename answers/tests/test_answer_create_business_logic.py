import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from questions.models import Question

User = get_user_model()


class AnswerCreateBusinessLogicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create different types of questions to test business logic
        self.private_question = Question.objects.create(
            title='Private Question',
            body='This is a private question',
            owner=self.user,
            is_public=False,
            status=Question.STATUS_PENDING
        )

        self.public_pending_question = Question.objects.create(
            title='Public Pending Question',
            body='This is a public question pending approval',
            owner=self.user,
            is_public=True,
            status=Question.STATUS_PENDING
        )

        self.public_denied_question = Question.objects.create(
            title='Public Denied Question',
            body='This is a public question that was denied',
            owner=self.user,
            is_public=True,
            status=Question.STATUS_DENIED
        )

        self.public_approved_question = Question.objects.create(
            title='Public Approved Question',
            body='This is an approved public question',
            owner=self.user,
            is_public=True,
            status=Question.STATUS_APPROVED
        )

    def test_can_create_answer_for_private_question(self):
        """Users can create answers for private questions"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:create', kwargs={
                      'question_id': self.private_question.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Look for text specific to the answer create page
        self.assertContains(response, 'Your Star Answer',
                            msg_prefix="Expected answer create page content")

    def test_can_create_answer_for_public_pending_question(self):
        """Users can create answers for public questions that are still pending approval"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:create', kwargs={
                      'question_id': self.public_pending_question.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Star Answer')

    def test_can_create_answer_for_public_denied_question(self):
        """Users can create answers for public questions that were denied"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:create', kwargs={
                      'question_id': self.public_denied_question.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Star Answer')

    def test_cannot_create_answer_for_public_approved_question(self):
        """Users cannot create answers for approved public questions"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:create', kwargs={
                      'question_id': self.public_approved_question.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Cannot Create Answer', status_code=404)
        self.assertContains(
            response, 'Public questions are designed to be used as read-only examples', status_code=404)

    def test_business_logic_is_visible_publicly_property(self):
        """Test that the is_visible_publicly property works correctly"""
        # Private question - not visible publicly
        self.assertFalse(self.private_question.is_visible_publicly)

        # Public pending - not visible publicly (not approved yet)
        self.assertFalse(self.public_pending_question.is_visible_publicly)

        # Public denied - not visible publicly (was denied)
        self.assertFalse(self.public_denied_question.is_visible_publicly)

        # Public approved - IS visible publicly
        self.assertTrue(self.public_approved_question.is_visible_publicly)
