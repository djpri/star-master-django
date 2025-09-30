import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestQuestionCreateView:
    """Test the question_create view and query parameter handling."""

    def test_create_view_requires_login(self, client):
        # Create and login a user
        User.objects.create_user(
            username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')

        # Access the create view with ?public=true
        url = reverse('questions:create') + '?public=true'
        response = client.get(url)

        assert response.status_code == 200
        # Check that the form has is_public initialized to True
        assert response.context['form'].initial.get('is_public') is True
        # Check that the template receives the is_public_question flag
        assert response.context['is_public_question'] is True

    def test_create_view_sets_is_public_false_with_query_param(self, client):
        # Create and login a user
        User.objects.create_user(
            username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')

        # Access the create view with ?public=false
        url = reverse('questions:create') + '?public=false'
        response = client.get(url)

        assert response.status_code == 200
        # Check that the form has is_public initialized to False
        assert response.context['form'].initial.get('is_public') is False
        # Check that the template receives the is_public_question flag
        assert response.context['is_public_question'] is False

    def test_create_view_without_query_param(self, client):
        # Create and login a user
        User.objects.create_user(
            username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')

        # Access the create view without query parameter
        url = reverse('questions:create')
        response = client.get(url)

        assert response.status_code == 200
        # Check that the form has no initial value for is_public
        assert 'is_public' not in response.context['form'].initial
        # Check that the template receives is_public_question as False
        assert response.context['is_public_question'] is False

    def test_create_view_with_invalid_query_param(self, client):
        # Create and login a user
        User.objects.create_user(
            username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')

        # Access the create view with invalid query parameter
        url = reverse('questions:create') + '?public=invalid'
        response = client.get(url)

        assert response.status_code == 200
        # Check that the form has no initial value for is_public
        assert 'is_public' not in response.context['form'].initial
        # Check that the template receives is_public_question as False
        assert response.context['is_public_question'] is False
        assert response.context['form'].initial.get('is_public') is True
        # Check that the template receives the is_public_question flag
        assert response.context['is_public_question'] is True

    def test_create_view_sets_is_public_false_with_query_param(self, client):
        """Verify that ?public=false initializes is_public field to False."""
        # Create and login a user
        User.objects.create_user(
            username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        # Access the create view with ?public=false
        url = reverse('questions:create') + '?public=false'
        response = client.get(url)
        assert response.status_code == 200
        # Check that the form has is_public initialized to False
        assert response.context['form'].initial.get('is_public') is False
        # Check that the template receives the is_public_question flag
        assert response.context['is_public_question'] is False

    def test_create_view_without_query_param(self, client):
        """Verify that without query param, is_public is not set."""
        # Create and login a user
        User.objects.create_user(
            username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        # Access the create view without query parameter
        url = reverse('questions:create')
        response = client.get(url)
        assert response.status_code == 200
        # Check that the form has no initial value for is_public
        assert 'is_public' not in response.context['form'].initial
        # Check that the template receives is_public_question as False
        assert response.context['is_public_question'] is False

    def test_create_view_with_invalid_query_param(self, client):
        """Verify that invalid query param values are ignored."""
        # Create and login a user
        User.objects.create_user(
            username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        # Access the create view with invalid query parameter
        url = reverse('questions:create') + '?public=invalid'
        response = client.get(url)
        assert response.status_code == 200
        # Check that the form has no initial value for is_public
        assert 'is_public' not in response.context['form'].initial
        # Check that the template receives is_public_question as False
        assert response.context['is_public_question'] is False
