from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def home(request):
    """Home page view"""
    return render(request, 'home.html')


@login_required
def profile(request):
    """User profile view showing favorited songs"""
    # This will be implemented when the Favorite model is available
    # For now, just show basic profile info
    context = {
        'user': request.user,
        'favorites': [],  # Will be populated later when favorites are implemented
    }
    return render(request, 'account/profile.html', context)
