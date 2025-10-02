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


@pytest.mark.django_db
class TestPublicQuestionListView:
    def test_admin_sees_pending_section_when_pending_questions_exist(self, client):
        admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )

        Question.objects.create(
            owner=admin_user,
            title='Pending community question',
            body='Describe a situation where you led a team.',
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password='adminpass123')

        response = client.get(reverse('questions:public_list'))

        assert response.status_code == 200
        assert 'Pending Questions' in response.content.decode()


@pytest.mark.django_db
class TestApprovePublicQuestionView:
    def test_admin_can_approve_pending_question(self, client):
        admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        owner = User.objects.create_user(
            username='owner', password='ownerpass123'
        )

        question = Question.objects.create(
            owner=owner,
            title='Pending leadership question',
            body='Tell me about a time you led a project.',
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password='adminpass123')

        response = client.post(
            reverse('questions:approve_public', args=[question.pk]),
            HTTP_ACCEPT='application/json'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        question.refresh_from_db()
        assert question.status == Question.STATUS_APPROVED

    def test_non_admin_cannot_approve_pending_question(self, client):
        owner = User.objects.create_user(
            username='owner', password='ownerpass123'
        )
        other_user = User.objects.create_user(
            username='viewer', password='viewerpass123'
        )

        question = Question.objects.create(
            owner=owner,
            title='Pending behavioral question',
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=other_user.username, password='viewerpass123')

        response = client.post(
            reverse('questions:approve_public', args=[question.pk]),
            HTTP_ACCEPT='application/json'
        )

        assert response.status_code == 403
        data = response.json()
        assert 'error' in data

        question.refresh_from_db()
        assert question.status == Question.STATUS_PENDING

    def test_post_without_json_accept_redirects_to_public_list(self, client):
        admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        owner = User.objects.create_user(
            username='owner', password='ownerpass123'
        )

        question = Question.objects.create(
            owner=owner,
            title='Pending redirect question',
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password='adminpass123')

        response = client.post(
            reverse('questions:approve_public', args=[question.pk]),
            data={'next': reverse('questions:public_list')}
        )

        assert response.status_code == 302
        assert response['Location'] == reverse('questions:public_list')

        question.refresh_from_db()
        assert question.status == Question.STATUS_APPROVED


@pytest.mark.django_db
class TestDenyPublicQuestionView:
    def test_admin_can_deny_pending_question(self, client):
        admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        owner = User.objects.create_user(
            username='owner', password='ownerpass123'
        )

        question = Question.objects.create(
            owner=owner,
            title='Pending denial question',
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password='adminpass123')

        response = client.post(
            reverse('questions:deny_public', args=[question.pk]),
            HTTP_ACCEPT='application/json'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        question.refresh_from_db()
        assert question.status == Question.STATUS_DENIED

    def test_non_admin_cannot_deny_pending_question(self, client):
        owner = User.objects.create_user(
            username='owner', password='ownerpass123'
        )
        other_user = User.objects.create_user(
            username='viewer', password='viewerpass123'
        )

        question = Question.objects.create(
            owner=owner,
            title='Pending denial attempt',
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=other_user.username, password='viewerpass123')

        response = client.post(
            reverse('questions:deny_public', args=[question.pk]),
            HTTP_ACCEPT='application/json'
        )

        assert response.status_code == 403
        data = response.json()
        assert 'error' in data

        question.refresh_from_db()
        assert question.status == Question.STATUS_PENDING

    def test_html_request_redirects_after_denial(self, client):
        admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        owner = User.objects.create_user(
            username='owner', password='ownerpass123'
        )

        question = Question.objects.create(
            owner=owner,
            title='Redirect denial question',
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password='adminpass123')

        response = client.post(
            reverse('questions:deny_public', args=[question.pk]),
            data={'next': reverse('questions:public_list')}
        )

        assert response.status_code == 302
        assert response['Location'] == reverse('questions:public_list')

        question.refresh_from_db()
        assert question.status == Question.STATUS_DENIED


@pytest.mark.django_db
class TestQuestionDetailView:
    def test_admin_can_view_pending_public_question(self, client):
        admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        owner = User.objects.create_user(
            username='owner', password='ownerpass123'
        )

        question = Question.objects.create(
            owner=owner,
            title='Pending situation question',
            body='Describe a situation you handled pending approval.',
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=admin_user.username, password='adminpass123')

        response = client.get(reverse('questions:detail', args=[question.pk]))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Approve Question' in content
        assert 'Deny Question' in content
        assert 'Community Question Template' not in content

    def test_non_admin_gets_404_for_pending_public_question(self, client):
        owner = User.objects.create_user(
            username='owner', password='ownerpass123'
        )
        other_user = User.objects.create_user(
            username='viewer', password='viewerpass123'
        )

        question = Question.objects.create(
            owner=owner,
            title='Pending task question',
            is_public=True,
            status=Question.STATUS_PENDING,
        )

        client.login(username=other_user.username, password='viewerpass123')

        response = client.get(reverse('questions:detail', args=[question.pk]))

        assert response.status_code == 404

    def test_question_not_found_returns_404(self, client):
        user = User.objects.create_user(
            username='viewer', password='viewerpass123'
        )

        client.login(username=user.username, password='viewerpass123')

        response = client.get(reverse('questions:detail', args=[9999]))

        assert response.status_code == 404
