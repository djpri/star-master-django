import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from questions.models import Question, Tag


class QuestionEditViewTest(TestCase):
    """Test cases for question edit functionality."""

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

        # Create a private question
        self.private_question = Question.objects.create(
            title='Test Private Question',
            body='This is a test private question body.',
            owner=self.user,
            is_public=False,
            status=Question.STATUS_PENDING
        )

        # Create a public question
        self.public_question = Question.objects.create(
            title='Test Public Question',
            body='This is a test public question body.',
            owner=self.user,
            is_public=True,
            status=Question.STATUS_APPROVED
        )

        # Create a test tag
        self.tag = Tag.objects.create(name='test-tag', owner=self.user)

    def test_edit_private_question_get(self):
        """Test GET request to edit a private question."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('questions:edit', kwargs={
                      'pk': self.private_question.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Interview Question')
        self.assertContains(response, self.private_question.title)
        self.assertContains(response, self.private_question.body)
        self.assertContains(
            response, 'border-dashed border-accent')  # Edit styling

    def test_edit_private_question_post_success(self):
        """Test successful POST request to edit a private question."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('questions:edit', kwargs={
                      'pk': self.private_question.pk})

        form_data = {
            'title': 'Updated Question Title',
            'body': 'Updated question body content.',
            'is_public': False
        }

        response = self.client.post(url, form_data)

        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'questions:detail', kwargs={'pk': self.private_question.pk}))

        # Check question was updated
        self.private_question.refresh_from_db()
        self.assertEqual(self.private_question.title, 'Updated Question Title')
        self.assertEqual(self.private_question.body,
                         'Updated question body content.')
        self.assertFalse(self.private_question.is_public)

    def test_edit_public_question_forbidden(self):
        """Test that public questions cannot be edited."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('questions:edit', kwargs={'pk': self.public_question.pk})

        response = self.client.get(url)

        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'questions:detail', kwargs={'pk': self.public_question.pk}))

    def test_edit_question_requires_login(self):
        """Test that editing requires user to be logged in."""
        url = reverse('questions:edit', kwargs={
                      'pk': self.private_question.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_edit_question_requires_ownership(self):
        """Test that users can only edit their own questions."""
        self.client.login(username='otheruser', password='otherpass123')
        url = reverse('questions:edit', kwargs={
                      'pk': self.private_question.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_nonexistent_question(self):
        """Test editing a question that doesn't exist."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('questions:edit', kwargs={'pk': 99999})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
