"""
Pytest configuration and shared fixtures for the entire test suite.

This file provides common fixtures that can be used across all test modules,
reducing duplication and making tests more maintainable.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


# User Fixtures
# These use function scope (default) because database state should be
# isolated between tests. However, centralizing them here avoids code duplication.

@pytest.fixture
def user(db):
    """Create a basic test user.

    This is a commonly used fixture that creates a user with standard credentials.
    Scope: function (default) - creates a new user for each test to ensure isolation.
    """
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin/superuser for testing admin functionality.

    Scope: function (default) - creates a new admin for each test.
    """
    return User.objects.create_user(
        username='adminuser',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def other_user(db):
    """Create a second user for testing multi-user scenarios.

    Useful for tests that need to verify permissions/ownership.
    Scope: function (default).
    """
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='testpass123'
    )


# Authenticated Client Fixtures

@pytest.fixture
def authenticated_client(client, user):
    """Provide a client that's already logged in as a regular user.

    This saves the common step of logging in at the start of each test.
    """
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Provide a client that's already logged in as an admin.

    Useful for testing admin-only views and functionality.
    """
    client.force_login(admin_user)
    return client


# Note on Fixture Scopes:
#
# We're intentionally NOT using broader scopes (session/module) for database
# fixtures because:
#
# 1. Test isolation is critical - tests should not affect each other
# 2. Database state can leak between tests with broader scopes
# 3. The --reuse-db flag already provides speed benefits for database setup
# 4. MD5 password hasher makes user creation fast enough
#
# If you find tests are still slow, profile them to find the actual bottleneck
# rather than risking test reliability with broader fixture scopes.
