import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from questions.models import Question

User = get_user_model()


@pytest.mark.django_db
class TestQuestionCreateView:
    """Test the question_create view and query parameter handling."""

    def test_create_view_sets_is_public_true_with_query_param(self, client):
        user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        client.login(username=user.username, password='testpass123')

        response = client.get(reverse('questions:create') + '?public=true')

        assert response.status_code == 200
        assert response.context['form'].initial.get('is_public') is True
        assert response.context['is_public_question'] is True

    def test_create_view_sets_is_public_false_with_query_param(self, client):
        user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        client.login(username=user.username, password='testpass123')

        response = client.get(reverse('questions:create') + '?public=false')

        assert response.status_code == 200
        assert response.context['form'].initial.get('is_public') is False
        assert response.context['is_public_question'] is False

    def test_create_view_without_query_param(self, client):
        user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        client.login(username=user.username, password='testpass123')

        response = client.get(reverse('questions:create'))

        assert response.status_code == 200
        assert 'is_public' not in response.context['form'].initial
        assert response.context['is_public_question'] is False

    def test_create_view_with_invalid_query_param(self, client):
        user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        client.login(username=user.username, password='testpass123')

        response = client.get(reverse('questions:create') + '?public=invalid')

        assert response.status_code == 200
        assert 'is_public' not in response.context['form'].initial
        assert response.context['is_public_question'] is False


@pytest.mark.django_db
class TestSavePublicQuestionView:
    def test_post_save_redirects_to_next_and_creates_copy(self, client):
        owner = User.objects.create_user(
            username='owner', password='ownerpass123'
        )
        public_question = Question.objects.create(
            owner=owner,
            title='Tell me about a challenge',
            body='Describe a situation...',
            is_public=True,
            status=Question.STATUS_APPROVED,
        )

        viewer = User.objects.create_user(
            username='viewer', password='viewerpass123'
        )
        client.login(username=viewer.username, password='viewerpass123')

        next_url = reverse('questions:detail', args=[public_question.pk])
        response = client.post(
            reverse('questions:save_public', args=[public_question.pk]),
            data={'next': next_url},
        )

        assert response.status_code == 302
        assert response['Location'] == next_url
        assert Question.objects.filter(
            owner=viewer,
            title=public_question.title,
            is_public=False,
        ).exists()

    def test_get_save_public_question_is_not_allowed(self, client):
        owner = User.objects.create_user(
            username='author', password='authorpass123'
        )
        public_question = Question.objects.create(
            owner=owner,
            title='Example question',
            is_public=True,
            status=Question.STATUS_APPROVED,
        )

        reader = User.objects.create_user(
            username='reader', password='readerpass123'
        )
        client.login(username=reader.username, password='readerpass123')

        response = client.get(
            reverse('questions:save_public', args=[public_question.pk])
        )

        assert response.status_code == 405
