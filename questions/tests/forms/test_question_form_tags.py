import pytest
from django.contrib.auth import get_user_model

from questions.forms import QuestionForm
from questions.models import Question, Tag

User = get_user_model()


@pytest.mark.django_db
class TestQuestionFormTagFunctionality:
    """Test tag creation, selection, and association with questions."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    @pytest.fixture
    def other_user(self):
        """Create another test user."""
        return User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )

    @pytest.fixture
    def public_tag(self):
        """Create a public tag."""
        return Tag.objects.create(
            name="Leadership",
            slug="leadership",
            is_public=True,
            owner=None,
        )

    @pytest.fixture
    def personal_tag(self, user):
        """Create a personal tag for the test user."""
        return Tag.objects.create(
            name="MyPersonalTag",
            slug="mypersonaltag",
            is_public=False,
            owner=user,
        )

    def test_form_creates_new_personal_tag_when_saving(self, user):
        """Test that new tags are created as personal tags for the user."""
        form_data = {
            "title": "Test Question",
            "body": "Test body",
            "is_public": False,
            "tags_input": "NewTag",
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        tag = Tag.objects.filter(name="NewTag").first()
        assert tag is not None
        assert tag.is_public is False
        assert tag.owner == user
        assert tag.slug == "newtag"
        assert tag in question.tags.all()

    def test_form_uses_existing_public_tag(self, user, public_tag):
        """Test that existing public tags are reused instead of creating duplicates."""
        initial_tag_count = Tag.objects.count()

        form_data = {
            "title": "Test Question",
            "body": "Test body",
            "is_public": False,
            "tags_input": "Leadership",
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        assert Tag.objects.count() == initial_tag_count
        assert public_tag in question.tags.all()

    def test_form_uses_existing_personal_tag(self, user, personal_tag):
        """Test that existing personal tags are reused instead of creating duplicates."""
        initial_tag_count = Tag.objects.count()

        form_data = {
            "title": "Test Question",
            "body": "Test body",
            "is_public": False,
            "tags_input": "MyPersonalTag",
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        assert Tag.objects.count() == initial_tag_count
        assert personal_tag in question.tags.all()

    def test_form_tag_lookup_is_case_insensitive(self, user, public_tag):
        """Test that tag lookup is case-insensitive."""
        form_data = {
            "title": "Test Question",
            "body": "Test body",
            "is_public": False,
            "tags_input": "leadership",
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        assert public_tag in question.tags.all()

    def test_form_can_mix_existing_and_new_tags(self, user, public_tag, personal_tag):
        """Test that a form can use both existing and new tags together."""
        form_data = {
            "title": "Test Question",
            "body": "Test body",
            "is_public": False,
            "tags_input": "Leadership,MyPersonalTag,BrandNewTag",
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        assert public_tag in question.tags.all()
        assert personal_tag in question.tags.all()

        new_tag = Tag.objects.filter(name="BrandNewTag", owner=user).first()
        assert new_tag is not None
        assert new_tag in question.tags.all()
        assert question.tags.count() == 3

    def test_form_handles_empty_tag_input(self, user):
        """Test that empty tag input doesn't create tags."""
        form_data = {
            "title": "Test Question",
            "body": "Test body",
            "is_public": False,
            "tags_input": "",
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        assert question.tags.count() == 0

    def test_form_ignores_duplicate_tags_in_input(self, user):
        """Test that duplicate tag names in input are handled correctly."""
        form_data = {
            "title": "Test Question",
            "body": "Test body",
            "is_public": False,
            "tags_input": "Tag1,Tag1,Tag2",
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        assert Tag.objects.filter(name="Tag1", owner=user).count() == 1
        assert Tag.objects.filter(name="Tag2", owner=user).count() == 1
        assert question.tags.count() == 2

    def test_form_does_not_use_other_users_personal_tags(self, user, other_user):
        """Test that one user cannot use another user's personal tags."""
        other_tag = Tag.objects.create(
            name="OtherUserTag",
            slug="otherusertag",
            is_public=False,
            owner=other_user,
        )

        form_data = {
            "title": "Test Question",
            "body": "Test body",
            "is_public": False,
            "tags_input": "OtherUserTag",
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        user_tag = Tag.objects.filter(name="OtherUserTag", owner=user).first()
        assert user_tag is not None
        assert user_tag != other_tag
        assert user_tag in question.tags.all()
        assert other_tag not in question.tags.all()

    def test_form_prepopulates_tags_when_editing(self, user, public_tag, personal_tag):
        """Test that tags_input is pre-populated when editing an existing question."""
        question = Question.objects.create(
            title="Test Question",
            body="Test body",
            owner=user,
            is_public=False,
        )
        question.tags.add(public_tag, personal_tag)

        form = QuestionForm(instance=question, user=user)

        tags_input_value = form.fields["tags_input"].initial
        assert "Leadership" in tags_input_value
        assert "MyPersonalTag" in tags_input_value

    def test_form_without_user_does_not_create_tags(self, user):
        """Test that tags are not created if no user is provided to the form."""
        form_data = {
            "title": "Test Question",
            "body": "Test body",
            "is_public": False,
            "tags_input": "Tag1,Tag2",
        }
        form = QuestionForm(data=form_data)
        assert form.is_valid(), form.errors

        initial_tag_count = Tag.objects.count()

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        assert Tag.objects.count() == initial_tag_count
        assert question.tags.count() == 0
