from django import forms
from django.utils.text import slugify

from .models import Question, Tag


class QuestionForm(forms.ModelForm):
    """Form for creating and editing questions with consistent styling."""

    # Custom field for tag selection and creation
    tags_input = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={
            'id': 'tags-input',
        }),
        label='Tags',
        help_text='Select existing tags or create new ones to organize your questions.',
    )

    class Meta:
        model = Question
        fields = ["title", "body", "is_public", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Write a concise interview question...",
                "maxlength": Question._meta.get_field("title").max_length,
            }),
            "body": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 6,
                "placeholder": "Add optional context or clarification for your question...",
            }),
            "is_public": forms.HiddenInput(),
            "tags": forms.MultipleHiddenInput(),
        }
        labels = {
            "title": "Question Title",
            "body": "Description (optional)",
            "is_public": "",  # Hidden field, no label needed
            "tags": "",  # Hidden field, handled by tags_input
        }
        help_texts = {
            "title": "Keep it focused so you can craft targeted answers.",
            "body": "Provide extra details or prompts that help with answering this question.",
            "is_public": "",  # Hidden field, no help text needed
            "tags": "",  # Hidden field, handled by tags_input
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Ensure consistent DaisyUI styling for required asterisk handling and errors via CSS classes.
        for field_name, field in self.fields.items():
            css_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_classes}".strip()
            if field.required:
                field.widget.attrs.setdefault("aria-required", "true")

        # Pre-populate tags_input if editing existing question
        if self.instance and self.instance.pk:
            tag_names = list(self.instance.tags.values_list('name', flat=True))
            self.fields['tags_input'].initial = ','.join(tag_names)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # Handle tags - only after instance is saved (needs ID for M2M)
            if self.user:
                tags_str = self.cleaned_data.get('tags_input', '')
                tag_names = [name.strip()
                             for name in tags_str.split(',') if name.strip()]

                tags_to_add = []
                for tag_name in tag_names:
                    # First, try to find a public tag
                    tag = Tag.objects.filter(
                        name__iexact=tag_name, is_public=True).first()

                    # If no public tag, try to find user's personal tag
                    if not tag and self.user:
                        tag = Tag.objects.filter(
                            name__iexact=tag_name, owner=self.user, is_public=False).first()

                    # If still no tag, create a new personal tag for the user
                    if not tag and self.user:
                        tag = Tag.objects.create(
                            name=tag_name,
                            slug=slugify(tag_name),
                            owner=self.user,
                            is_public=False
                        )

                    if tag:
                        tags_to_add.append(tag)

                instance.tags.set(tags_to_add)

        return instance
