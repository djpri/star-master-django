import pytest

from questions.forms import QuestionForm


@pytest.fixture
def form():
    return QuestionForm()


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
def test_question_form_widgets_use_consistent_styles(form, field_name, expected_class):
    assert expected_class in form.fields[field_name].widget.attrs.get(
        "class", "")


def test_question_form_is_public_is_hidden(form):
    """Verify that is_public field uses HiddenInput widget."""
    from django.forms.widgets import HiddenInput

    assert isinstance(form.fields["is_public"].widget, HiddenInput)


def test_question_form_help_text_guidance(form):
    assert "focused" in form.fields["title"].help_text
    # is_public is now a hidden field with no help text
    assert form.fields["is_public"].help_text == ""
