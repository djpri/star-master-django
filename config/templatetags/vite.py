import json
import os
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def vite_asset(entry_name):
    """
    Load CSS or JS files through Vite.

    In development: Points to Vite dev server
    In production: Points to built files using Vite's manifest + Django's static resolution
    """

    # DEVELOPMENT MODE: Use Vite dev server
    if settings.DEBUG:
        # Try to detect Vite dev server port (default 5173, fallback 5174)
        vite_port = getattr(settings, 'VITE_DEV_PORT', '5173')

        if entry_name.endswith('.css'):
            # For CSS files, load them through Vite dev server
            return mark_safe(f'<link rel="stylesheet" href="http://localhost:{vite_port}/static/css/{entry_name}">')
        else:
            # For JS files, load them as modules
            return mark_safe(f'<script type="module" src="http://localhost:{vite_port}/static/js/{entry_name}"></script>')

    # PRODUCTION MODE: Use built files with manifest
    else:
        try:
            # Read Vite's manifest file from the correct location
            manifest_path = os.path.join(
                settings.BASE_DIR, 'static', 'dist', '.vite', 'manifest.json')

            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)

                # Look for the entry in the manifest
                entry_key = f'static/css/{entry_name}' if entry_name.endswith(
                    '.css') else f'static/js/{entry_name}'

                if entry_key in manifest:
                    entry = manifest[entry_key]
                    built_file = entry.get('file', '')

                    if built_file:
                        # Use Django's static() function to resolve the final hashed filename
                        asset_url = static(built_file)

                        if entry_name.endswith('.css'):
                            return mark_safe(f'<link rel="stylesheet" href="{asset_url}">')
                        else:
                            return mark_safe(f'<script type="module" src="{asset_url}"></script>')
                else:
                    print(
                        f"Entry '{entry_key}' not found in manifest. Available entries: {list(manifest.keys())}")
            else:
                print(f"Manifest file not found at: {manifest_path}")

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Vite manifest error: {e}")

        # Fallback for production if manifest fails
        if entry_name.endswith('.css'):
            return mark_safe(f'<!-- Vite CSS not found: {entry_name} -->')
        else:
            return mark_safe(f'<!-- Vite JS not found: {entry_name} -->')


@register.simple_tag
def vite_hmr():
    """
    Include Vite's hot reload client in development mode.
    This enables automatic page refresh when you save files.
    """
    if settings.DEBUG:
        vite_port = getattr(settings, 'VITE_DEV_PORT', '5173')
        return mark_safe(f'<script type="module" src="http://localhost:{vite_port}/@vite/client"></script>')
    return ''
