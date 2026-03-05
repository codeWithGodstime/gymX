#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Modify startapp to default to apps/ directory
    if len(sys.argv) > 1 and sys.argv[1] == 'startapp' and '--directory' not in sys.argv:
        idx = sys.argv.index('startapp')
        if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith('-'):
            sys.argv.insert(idx + 2, '--directory')
            sys.argv.insert(idx + 3, 'apps')
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gymx.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
