#!/usr/bin/env python
"""
Test script to verify production template tags work correctly
"""
from config.templatetags.vite import vite_asset, vite_hmr
import os
import sys
import django
from django.conf import settings

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

# Import template tags after Django setup


def test_production_mode():
    """Test template tags in production mode"""

    print("=== TESTING PRODUCTION MODE ===")

    # Temporarily set DEBUG to False to test production mode
    original_debug = settings.DEBUG
    settings.DEBUG = False

    try:
        # Test CSS loading
        print("\n1. Testing CSS asset loading:")
        css_output = vite_asset('input.css')
        print(f"CSS Output: {css_output}")

        # Test JS loading
        print("\n2. Testing JS asset loading:")
        js_output = vite_asset('main.js')
        print(f"JS Output: {js_output}")

        # Test HMR (should be empty in production)
        print("\n3. Testing HMR (should be empty):")
        hmr_output = vite_hmr()
        print(f"HMR Output: '{hmr_output}'")

        # Check if CSS output contains the hashed filename
        if 'style.iqdFhmNN.css' in str(css_output):
            print("\n✅ SUCCESS: CSS asset correctly loads hashed file!")
        else:
            print("\n❌ ERROR: CSS asset not loading correctly")

        # Check if JS output contains the hashed filename
        if 'main-B0zW7jOa.js' in str(js_output):
            print("✅ SUCCESS: JS asset correctly loads hashed file!")
        else:
            print("❌ ERROR: JS asset not loading correctly")

    finally:
        # Restore original DEBUG setting
        settings.DEBUG = original_debug


def test_development_mode():
    """Test template tags in development mode"""

    print("\n\n=== TESTING DEVELOPMENT MODE ===")

    # Ensure DEBUG is True for development testing
    original_debug = settings.DEBUG
    settings.DEBUG = True

    try:
        # Test CSS loading
        print("\n1. Testing CSS asset loading:")
        css_output = vite_asset('input.css')
        print(f"CSS Output: {css_output}")

        # Test HMR
        print("\n2. Testing HMR:")
        hmr_output = vite_hmr()
        print(f"HMR Output: {hmr_output}")

        # Check if development mode uses localhost
        if 'localhost:5174' in str(css_output):
            print("\n✅ SUCCESS: Development mode correctly uses localhost!")
        else:
            print("\n❌ ERROR: Development mode not using localhost correctly")

    finally:
        # Restore original DEBUG setting
        settings.DEBUG = original_debug


if __name__ == '__main__':
    print("Testing Vite Template Tags for Production Deployment")
    print("=" * 60)

    # Check if manifest file exists
    manifest_path = os.path.join(
        settings.BASE_DIR, 'static', 'dist', '.vite', 'manifest.json')
    if os.path.exists(manifest_path):
        print("✅ Vite manifest file found!")
    else:
        print("❌ Vite manifest file missing!")
        print(f"Expected at: {manifest_path}")

    test_production_mode()
    test_development_mode()

    print("\n" + "=" * 60)
    print("Testing complete!")
