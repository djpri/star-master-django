import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from questions.models import Question
from answers.models import StarAnswer, BasicAnswer

User = get_user_model()


class AnswerCreateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.private_question = Question.objects.create(
            title='Private Question',
            body='This is a private question',
            owner=self.user,
            is_public=False,
            status=Question.STATUS_PENDING
        )

    def test_create_star_answer_sets_is_public_false(self):
        """Creating a STAR answer automatically sets is_public to False"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:create', kwargs={
                      'question_id': self.private_question.pk})

        response = self.client.post(url, {
            'answer_type': 'STAR',
            'situation': 'Test situation',
            'task': 'Test task',
            'action': 'Test action',
            'result': 'Test result'
        })

        # Redirect after successful creation
        self.assertEqual(response.status_code, 302)

        # Check that answer was created with is_public=False
        answer = StarAnswer.objects.get(
            question=self.private_question, user=self.user)
        self.assertFalse(answer.is_public)
        self.assertEqual(answer.situation, 'Test situation')

    def test_create_basic_answer_sets_is_public_false(self):
        """Creating a Basic answer automatically sets is_public to False"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('answers:create', kwargs={
                      'question_id': self.private_question.pk})

        response = self.client.post(url, {
            'answer_type': 'BASIC',
            'text': 'This is my basic answer'
        })

        # Redirect after successful creation
        self.assertEqual(response.status_code, 302)

        # Check that answer was created with is_public=False
        answer = BasicAnswer.objects.get(
            question=self.private_question, user=self.user)
        self.assertFalse(answer.is_public)
        self.assertEqual(answer.text, 'This is my basic answer')
