import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from questions.models import Question
from answers.models import Answer, StarAnswer, BasicAnswer


class AnswerEditViewTest(TestCase):
    """Test cases for answer edit functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        # Create a private question for testing
        self.question = Question.objects.create(
            title='Test Question',
            body='This is a test question.',
            owner=self.user,
            is_public=False,
            status=Question.STATUS_PENDING
        )

        # Create a STAR answer
        self.star_answer = StarAnswer.objects.create(
            question=self.question,
            user=self.user,
            situation='Test situation',
            task='Test task',
            action='Test action',
            result='Test result',
            is_public=False
        )

        # Create a Basic answer
        self.basic_answer = BasicAnswer.objects.create(
            question=self.question,
            user=self.user,
            text='Test basic answer text',
            is_public=False
        )

    def test_edit_star_answer_get(self):
        """Test GET request to edit a STAR answer."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:edit', kwargs={'pk': self.star_answer.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit STAR Answer')
        self.assertContains(response, 'Test situation')
        self.assertContains(response, 'Test task')
        self.assertContains(response, 'Test action')
        self.assertContains(response, 'Test result')
        self.assertContains(
            response, 'border-dashed border-accent')  # Edit styling

    def test_edit_basic_answer_get(self):
        """Test GET request to edit a basic answer."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:edit', kwargs={'pk': self.basic_answer.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit BASIC Answer')
        self.assertContains(response, 'Test basic answer text')
        self.assertContains(
            response, 'border-dashed border-accent')  # Edit styling

    def test_edit_star_answer_post_success(self):
        """Test successful POST request to edit a STAR answer."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:edit', kwargs={'pk': self.star_answer.pk})

        form_data = {
            'situation': 'Updated situation',
            'task': 'Updated task',
            'action': 'Updated action',
            'result': 'Updated result'
        }

        response = self.client.post(url, form_data)

        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'answers:detail', kwargs={'pk': self.star_answer.pk}))

        # Check answer was updated
        self.star_answer.refresh_from_db()
        self.assertEqual(self.star_answer.situation, 'Updated situation')
        self.assertEqual(self.star_answer.task, 'Updated task')
        self.assertEqual(self.star_answer.action, 'Updated action')
        self.assertEqual(self.star_answer.result, 'Updated result')
        self.assertFalse(self.star_answer.is_public)  # Should remain private

    def test_edit_basic_answer_post_success(self):
        """Test successful POST request to edit a basic answer."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:edit', kwargs={'pk': self.basic_answer.pk})

        form_data = {
            'text': 'Updated basic answer text'
        }

        response = self.client.post(url, form_data)

        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'answers:detail', kwargs={'pk': self.basic_answer.pk}))

        # Check answer was updated
        self.basic_answer.refresh_from_db()
        self.assertEqual(self.basic_answer.text, 'Updated basic answer text')
        self.assertFalse(self.basic_answer.is_public)  # Should remain private

    def test_edit_answer_requires_login(self):
        """Test that editing requires user to be logged in."""
        url = reverse('answers:edit', kwargs={'pk': self.star_answer.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_edit_answer_requires_ownership(self):
        """Test that users can only edit their own answers."""
        self.client.login(username='otheruser', password='otherpass123')
        url = reverse('answers:edit', kwargs={'pk': self.star_answer.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_nonexistent_answer(self):
        """Test editing an answer that doesn't exist."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:edit', kwargs={'pk': 99999})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_star_answer_form_validation(self):
        """Test form validation for STAR answer edit."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:edit', kwargs={'pk': self.star_answer.pk})

        # Submit form with missing required fields
        form_data = {
            'situation': '',  # Empty required field
            'task': 'Updated task',
            'action': 'Updated action',
            'result': 'Updated result'
        }

        response = self.client.post(url, form_data)

        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_edit_basic_answer_form_validation(self):
        """Test form validation for basic answer edit."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:edit', kwargs={'pk': self.basic_answer.pk})

        # Submit form with missing required fields
        form_data = {
            'text': ''  # Empty required field
        }

        response = self.client.post(url, form_data)

        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
