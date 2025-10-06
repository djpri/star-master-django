import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from questions.models import Question


class TestQuestionActionsMenuDisplay(TestCase):
    """Test that the question actions menu displays correctly in various contexts."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create users
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='ownerpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        # Create questions
        self.public_approved_question = Question.objects.create(
            title='Approved Public Question',
            body='This is approved.',
            owner=self.owner,
            is_public=True,
            status=Question.STATUS_APPROVED
        )

        self.public_pending_question = Question.objects.create(
            title='Pending Public Question',
            body='This is pending.',
            owner=self.owner,
            is_public=True,
            status=Question.STATUS_PENDING
        )

        self.private_question = Question.objects.create(
            title='Private Question',
            body='This is private.',
            owner=self.owner,
            is_public=False,
            status=Question.STATUS_PENDING
        )

    def test_owner_sees_menu_on_own_public_question_detail(self):
        """Test that question owner sees actions menu on their public question detail page."""
        self.client.login(username='owner', password='ownerpass123')
        response = self.client.get(reverse('questions:detail', kwargs={
                                   'pk': self.public_approved_question.pk}))

        self.assertEqual(response.status_code, 200)
        # Check for three-dots button (ellipsis icon)
        self.assertContains(response, 'fa-ellipsis-v')
        # Check for edit link
        self.assertContains(response, 'Edit Question')
        # Check for delete button
        self.assertContains(response, 'Delete Question')

    def test_admin_sees_menu_on_others_public_question_detail(self):
        """Test that admin sees actions menu on another user's public question."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('questions:detail', kwargs={
                                   'pk': self.public_approved_question.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'fa-ellipsis-v')
        self.assertContains(response, 'Edit Question')
        self.assertContains(response, 'Delete Question')

    def test_other_user_does_not_see_menu_on_public_question_detail(self):
        """Test that other users don't see actions menu on someone else's public question."""
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.get(reverse('questions:detail', kwargs={
                                   'pk': self.public_approved_question.pk}))

        self.assertEqual(response.status_code, 200)
        # Should not see the actions menu at all
        self.assertNotContains(response, 'Edit Question')
        self.assertNotContains(response, 'Delete Question')

    def test_owner_sees_menu_on_own_question_in_list(self):
        """Test that question owner sees actions menu on their questions in the question list."""
        self.client.login(username='owner', password='ownerpass123')
        response = self.client.get(reverse('questions:list'))

        self.assertEqual(response.status_code, 200)
        # Should see actions menu for their questions
        self.assertContains(response, 'fa-ellipsis-v')
        self.assertContains(response, 'Edit Question')

    def test_admin_sees_menu_on_public_question_in_public_list(self):
        """Test that admin sees actions menu on public questions in the public list."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('questions:public_list'))

        self.assertEqual(response.status_code, 200)
        # Admin should see actions menu
        self.assertContains(response, 'fa-ellipsis-v')

    def test_owner_sees_menu_on_pending_question_in_public_list(self):
        """Test that admin sees actions menu on pending questions in public list."""
        # Only admins can see pending questions in the public list
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('questions:public_list'))

        self.assertEqual(response.status_code, 200)
        # Should see pending section
        self.assertContains(response, 'Pending Questions')
        # Should see actions menu
        self.assertContains(response, 'fa-ellipsis-v')

    def test_anonymous_user_does_not_see_menu_on_public_question_detail(self):
        """Test that anonymous users don't see actions menu."""
        response = self.client.get(reverse('questions:detail', kwargs={
                                   'pk': self.public_approved_question.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Edit Question')
        self.assertNotContains(response, 'Delete Question')

    def test_other_user_does_not_see_menu_in_public_list(self):
        """Test that regular users don't see actions menu on others' public questions in list."""
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.get(reverse('questions:public_list'))

        self.assertEqual(response.status_code, 200)
        # Should see public questions but no actions menu
        self.assertNotContains(response, 'Edit Question')
        self.assertNotContains(response, 'Delete Question')
