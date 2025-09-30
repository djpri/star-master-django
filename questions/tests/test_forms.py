import pytest
from django.contrib.auth import get_user_model

from questions.forms import QuestionForm
from questions.models import Question, Tag

User = get_user_model()


# Original tests (keeping them intact)
def test_question_form_valid_without_description():
    form = QuestionForm(data={
        "title": "Tell me about a time you led a project",
        "body": "",
    })

    assert form.is_valid(), form.errors


def test_question_form_requires_title():
    form = QuestionForm(data={"body": "Optional body only"})

    assert not form.is_valid()
    assert "title" in form.errors


@pytest.mark.parametrize(
    "field_name, expected_class",
    [
        ("title", "input input-bordered w-full"),
        ("body", "textarea textarea-bordered w-full"),
    ],
)
def test_question_form_widgets_use_consistent_styles(field_name, expected_class):
    form = QuestionForm()

    assert expected_class in form.fields[field_name].widget.attrs.get(
        "class", "")


def test_question_form_is_public_is_hidden():
    """Verify that is_public field uses HiddenInput widget."""
    form = QuestionForm()

    from django.forms.widgets import HiddenInput
    assert isinstance(form.fields["is_public"].widget, HiddenInput)


def test_question_form_help_text_guidance():
    form = QuestionForm()

    assert "focused" in form.fields["title"].help_text
    # is_public is now a hidden field with no help text
    assert form.fields["is_public"].help_text == ""


# ============================================================================
# TAG FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.django_db
class TestQuestionFormTagFunctionality:
    """Test tag creation, selection, and association with questions."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @pytest.fixture
    def other_user(self):
        """Create another test user."""
        return User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

    @pytest.fixture
    def public_tag(self):
        """Create a public tag."""
        return Tag.objects.create(
            name='Leadership',
            slug='leadership',
            is_public=True,
            owner=None
        )

    @pytest.fixture
    def personal_tag(self, user):
        """Create a personal tag for the test user."""
        return Tag.objects.create(
            name='MyPersonalTag',
            slug='mypersonaltag',
            is_public=False,
            owner=user
        )


    def test_form_creates_new_personal_tag_when_saving(self, user):
        """Test that new tags are created as personal tags for the user."""
        form_data = {
            'title': 'Test Question',
            'body': 'Test body',
            'is_public': False,
            'tags_input': 'NewTag',
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        # Verify tag was created
        tag = Tag.objects.filter(name='NewTag').first()
        assert tag is not None
        assert tag.is_public is False
        assert tag.owner == user
        assert tag.slug == 'newtag'

        # Verify tag is associated with question
        assert tag in question.tags.all()


    def test_form_uses_existing_public_tag(self, user, public_tag):
        """Test that existing public tags are reused instead of creating duplicates."""
        initial_tag_count = Tag.objects.count()

        form_data = {
            'title': 'Test Question',
            'body': 'Test body',
            'is_public': False,
            'tags_input': 'Leadership',
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        # Verify no new tag was created
        assert Tag.objects.count() == initial_tag_count

        # Verify the existing public tag is used
        assert public_tag in question.tags.all()

    def test_form_uses_existing_personal_tag(self, user, personal_tag):
        """Test that existing personal tags are reused instead of creating duplicates."""
        initial_tag_count = Tag.objects.count()

        form_data = {
            'title': 'Test Question',
            'body': 'Test body',
            'is_public': False,
            'tags_input': 'MyPersonalTag',
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        # Verify no new tag was created
        assert Tag.objects.count() == initial_tag_count

        # Verify the existing personal tag is used
        assert personal_tag in question.tags.all()

    def test_form_tag_lookup_is_case_insensitive(self, user, public_tag):
        """Test that tag lookup is case-insensitive."""
        form_data = {
            'title': 'Test Question',
            'body': 'Test body',
            'is_public': False,
            'tags_input': 'leadership',
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        # Verify the existing public tag is used (case-insensitive match)
        assert public_tag in question.tags.all()

    def test_form_can_mix_existing_and_new_tags(self, user, public_tag, personal_tag):
        """Test that a form can use both existing and new tags together."""
        form_data = {
            'title': 'Test Question',
            'body': 'Test body',
            'is_public': False,
            'tags_input': 'Leadership,MyPersonalTag,BrandNewTag',
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        # Verify existing tags are reused
        assert public_tag in question.tags.all()
        assert personal_tag in question.tags.all()

        # Verify new tag was created
        new_tag = Tag.objects.filter(name='BrandNewTag', owner=user).first()
        assert new_tag is not None
        assert new_tag in question.tags.all()

        # Verify total tag count
        assert question.tags.count() == 3


    def test_form_handles_empty_tag_input(self, user):
        """Test that empty tag input doesn't create tags."""
        form_data = {
            'title': 'Test Question',
            'body': 'Test body',
            'is_public': False,
            'tags_input': '',
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        # Verify no tags were created
        assert question.tags.count() == 0

    def test_form_ignores_duplicate_tags_in_input(self, user):
        """Test that duplicate tag names in input are handled correctly."""
        form_data = {
            'title': 'Test Question',
            'body': 'Test body',
            'is_public': False,
            'tags_input': 'Tag1,Tag1,Tag2',
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        # Verify only unique tags are created
        assert Tag.objects.filter(name='Tag1', owner=user).count() == 1
        assert Tag.objects.filter(name='Tag2', owner=user).count() == 1
        assert question.tags.count() == 2

    def test_form_does_not_use_other_users_personal_tags(self, user, other_user):
        """Test that one user cannot use another user's personal tags."""
        # Create a personal tag for other_user
        other_tag = Tag.objects.create(
            name='OtherUserTag',
            slug='otherusertag',
            is_public=False,
            owner=other_user
        )

        form_data = {
            'title': 'Test Question',
            'body': 'Test body',
            'is_public': False,
            'tags_input': 'OtherUserTag',
        }
        form = QuestionForm(data=form_data, user=user)
        assert form.is_valid(), form.errors

        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        # Verify a new tag was created for this user (not reusing other's tag)
        user_tag = Tag.objects.filter(name='OtherUserTag', owner=user).first()
        assert user_tag is not None
        assert user_tag != other_tag
        assert user_tag in question.tags.all()
        assert other_tag not in question.tags.all()

    def test_form_prepopulates_tags_when_editing(self, user, public_tag, personal_tag):
        """Test that tags_input is pre-populated when editing an existing question."""
        # Create a question with tags
        question = Question.objects.create(
            title='Test Question',
            body='Test body',
            owner=user,
            is_public=False
        )
        question.tags.add(public_tag, personal_tag)

        # Create form with instance
        form = QuestionForm(instance=question, user=user)

        # Verify tags_input is pre-populated
        tags_input_value = form.fields['tags_input'].initial
        assert 'Leadership' in tags_input_value
        assert 'MyPersonalTag' in tags_input_value

    def test_form_without_user_does_not_create_tags(self, user):
        """Test that tags are not created if no user is provided to the form."""
        form_data = {
            'title': 'Test Question',
            'body': 'Test body',
            'is_public': False,
            'tags_input': 'Tag1,Tag2',
        }
        form = QuestionForm(data=form_data)  # No user provided to form
        assert form.is_valid(), form.errors

        initial_tag_count = Tag.objects.count()

        # We still need to set owner for the question to save
        question = form.save(commit=False)
        question.owner = user
        question = form.save()

        # Verify no tags were created (because form.user was None)
        assert Tag.objects.count() == initial_tag_count
        assert question.tags.count() == 0
