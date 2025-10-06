"""
Tests for filter and search functionality on question list page.
"""
import pytest
from django.urls import reverse
from questions.models import Question, Tag
from answers.models import BasicAnswer, StarAnswer
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestQuestionListFilterSearch:
    """Test filtering and searching on the question list page."""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @pytest.fixture
    def tags(self, user):
        """Create test tags."""
        public_tag = Tag.objects.create(
            name='Leadership', slug='leadership', is_public=True)
        private_tag = Tag.objects.create(
            name='MyTag', slug='mytag', is_public=False, owner=user)
        return {'public': public_tag, 'private': private_tag}

    @pytest.fixture
    def questions(self, user, tags):
        """Create test questions with tags."""
        q1 = Question.objects.create(
            owner=user,
            title='Question about leadership',
            body='How do you demonstrate leadership?'
        )
        q1.tags.add(tags['public'])

        q2 = Question.objects.create(
            owner=user,
            title='Question about teamwork',
            body='Describe a time you worked in a team'
        )
        q2.tags.add(tags['private'])

        q3 = Question.objects.create(
            owner=user,
            title='General question',
            body='Tell me about yourself'
        )

        return [q1, q2, q3]

    def test_filter_by_tag(self, client, user, questions, tags):
        """Test filtering questions by tag."""
        client.force_login(user)
        response = client.get(reverse('questions:list'), {'tag': 'Leadership'})

        assert response.status_code == 200
        assert questions[0] in response.context['questions']
        assert questions[1] not in response.context['questions']
        assert response.context['selected_tag'] == 'Leadership'

    def test_search_in_question_title(self, client, user, questions):
        """Test searching in question titles."""
        client.force_login(user)
        response = client.get(reverse('questions:list'),
                              {'search': 'leadership'})

        assert response.status_code == 200
        # Should find the question with 'leadership' in title
        assert questions[0] in response.context['questions']

    def test_search_in_answers(self, client, user, questions):
        """Test searching in answer content."""
        client.force_login(user)

        # Create an answer with specific content
        BasicAnswer.objects.create(
            question=questions[2],
            user=user,
            text='I have experience with Python programming'
        )

        response = client.get(reverse('questions:list'), {'search': 'Python'})

        assert response.status_code == 200
        # Should find the question that has an answer mentioning Python
        assert questions[2] in response.context['questions']

    def test_combined_filter_and_search(self, client, user, questions, tags):
        """Test using both tag filter and search together."""
        client.force_login(user)
        response = client.get(
            reverse('questions:list'),
            {'tag': 'Leadership', 'search': 'leadership'}
        )

        assert response.status_code == 200
        assert questions[0] in response.context['questions']
        assert response.context['selected_tag'] == 'Leadership'
        assert response.context['search_query'] == 'leadership'

    def test_pagination_preserves_filters(self, client, user, tags):
        """Test that pagination maintains filter and search parameters."""
        client.force_login(user)

        # Create enough questions to trigger pagination (>12)
        for i in range(15):
            q = Question.objects.create(
                owner=user,
                title=f'Question {i}',
                body='Test question'
            )
            if i % 2 == 0:
                q.tags.add(tags['public'])

        response = client.get(
            reverse('questions:list'),
            {'tag': 'Leadership', 'page': '1'}
        )

        assert response.status_code == 200
        # Check that pagination links preserve the tag filter
        assert 'tag=Leadership' in response.content.decode()

    def test_no_results_shows_zero_message(self, client, user):
        """Test that when search/filter returns no results, it shows '0 Questions found'."""
        client.force_login(user)

        # Create a question that won't match our search
        Question.objects.create(
            owner=user,
            title='Python Programming',
            body='How do you use Python?'
        )

        # Search for something that doesn't exist
        response = client.get(reverse('questions:list'), {
                              'search': 'zzzznonexistent'})

        assert response.status_code == 200
        content = response.content.decode()

        # Should show "0 Questions found"
        assert '0 Questions found' in content

        # Should NOT show the empty state message
        assert 'No Questions in Your Collection' not in content

        # Should still show the search box (filter bar is present)
        assert 'search=' in content or 'Filter by Tag' in content
