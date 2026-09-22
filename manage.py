#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def _free_port_if_needed():
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver' and os.environ.get('RUN_MAIN') != 'true':
        port = 8000
        for arg in sys.argv[2:]:
            if ':' in arg:
                try:
                    port = int(arg.split(':')[-1])
                except ValueError:
                    pass
            elif arg.isdigit():
                port = int(arg)
        try:
            import subprocess
            res = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                current_pid = str(os.getpid())
                for pid in res.stdout.strip().split():
                    if pid != current_pid:
                        try:
                            os.kill(int(pid), 9)
                        except (ProcessLookupError, PermissionError):
                            pass
        except Exception:
            pass


def main():
    """Run administrative tasks."""
    _free_port_if_needed()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
