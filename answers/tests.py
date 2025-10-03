import pytest
from django.contrib.auth import get_user_model
from questions.models import Question
from answers.models import Answer, StarAnswer, BasicAnswer

User = get_user_model()


@pytest.mark.django_db
class TestMultipleAnswers:
    """Test that users can create multiple answers for the same question"""

    def test_user_can_create_multiple_star_answers(self):
        """Test that a user can create multiple STAR answers for the same question"""
        # Create test user and question
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        question = Question.objects.create(
            title='Test Interview Question',
            body='Describe a challenging situation you faced.',
            owner=user,
            is_public=False
        )

        # Create first STAR answer
        star_answer_1 = StarAnswer.objects.create(
            question=question,
            user=user,
            situation='First situation',
            task='First task',
            action='First action',
            result='First result'
        )

        # Create second STAR answer for the same question
        star_answer_2 = StarAnswer.objects.create(
            question=question,
            user=user,
            situation='Second situation',
            task='Second task',
            action='Second action',
            result='Second result'
        )

        # Verify both answers exist
        assert Answer.objects.filter(
            question=question,
            user=user
        ).count() == 2

        # Verify they are different instances
        assert star_answer_1.pk != star_answer_2.pk
        assert star_answer_1.question == star_answer_2.question
        assert star_answer_1.user == star_answer_2.user

    def test_user_can_create_multiple_basic_answers(self):
        """Test that a user can create multiple Basic answers for the same question"""
        # Create test user and question
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        question = Question.objects.create(
            title='Test Interview Question',
            body='Describe a challenging situation you faced.',
            owner=user,
            is_public=False
        )

        # Create first Basic answer
        basic_answer_1 = BasicAnswer.objects.create(
            question=question,
            user=user,
            text='First basic answer text'
        )

        # Create second Basic answer for the same question
        basic_answer_2 = BasicAnswer.objects.create(
            question=question,
            user=user,
            text='Second basic answer text'
        )

        # Verify both answers exist
        assert Answer.objects.filter(
            question=question,
            user=user
        ).count() == 2

        # Verify they are different instances
        assert basic_answer_1.pk != basic_answer_2.pk

    def test_user_can_create_mixed_answer_types(self):
        """Test that a user can create both STAR and Basic answers for the same question"""
        # Create test user and question
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        question = Question.objects.create(
            title='Test Interview Question',
            body='Describe a challenging situation you faced.',
            owner=user,
            is_public=False
        )

        # Create a STAR answer
        star_answer = StarAnswer.objects.create(
            question=question,
            user=user,
            situation='A situation',
            task='A task',
            action='An action',
            result='A result'
        )

        # Create a Basic answer for the same question
        basic_answer = BasicAnswer.objects.create(
            question=question,
            user=user,
            text='A basic answer'
        )

        # Verify both answers exist
        answers = Answer.objects.filter(
            question=question,
            user=user
        )
        assert answers.count() == 2

        # Verify one is STAR and one is BASIC
        answer_types = set(answers.values_list('answer_type', flat=True))
        assert answer_types == {'STAR', 'BASIC'}

    def test_user_can_create_many_answers(self):
        """Test that a user can create many answers (>2) for the same question"""
        # Create test user and question
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        question = Question.objects.create(
            title='Test Interview Question',
            body='Describe a challenging situation you faced.',
            owner=user,
            is_public=False
        )

        # Create 5 answers
        for i in range(5):
            BasicAnswer.objects.create(
                question=question,
                user=user,
                text=f'Answer number {i + 1}'
            )

        # Verify all 5 answers exist
        assert Answer.objects.filter(
            question=question,
            user=user
        ).count() == 5
