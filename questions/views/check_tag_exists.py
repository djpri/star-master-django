from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import models
from questions.models import Tag


@login_required
def check_tag_exists(request):
    """
    AJAX endpoint to check if a tag name already exists for the current user.
    Returns the existing tag info if found, or indicates if it can be created.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method allowed'}, status=405)

    tag_name = request.GET.get('name', '').strip()

    if not tag_name:
        return JsonResponse({'error': 'Tag name is required'}, status=400)

    # Check if tag name already exists using the same logic as form save()
    # First, try to find a public tag
    existing_tag = Tag.objects.filter(
        name__iexact=tag_name, is_public=True
    ).first()

    # If no public tag, try to find user's personal tag
    if not existing_tag:
        existing_tag = Tag.objects.filter(
            name__iexact=tag_name,
            owner=request.user,
            is_public=False
        ).first()

    if existing_tag:
        return JsonResponse({
            'exists': True,
            'tag': {
                'id': existing_tag.pk,
                'name': existing_tag.name,
                'is_public': existing_tag.is_public,
                'can_use': True
            }
        })
    else:
        return JsonResponse({
            'exists': False,
            'can_create': True
        })
