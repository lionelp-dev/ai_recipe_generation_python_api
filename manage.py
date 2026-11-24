#!/usr/bin/env python
import os
import sys
from pathlib import Path

import environ


def configure_runserver_port():
    """Use PORT from .env when runserver has no explicit address or port."""
    if len(sys.argv) < 2 or sys.argv[1] != "runserver":
        return

    runserver_arguments = sys.argv[2:]

    # An explicit positional argument, e.g. `runserver 9001`, takes priority.
    if any(not argument.startswith("-") for argument in runserver_arguments):
        return

    env = environ.Env()
    environ.Env.read_env(Path(__file__).resolve().parent / ".env")
    port = env.int("PORT", default=8000)

    sys.argv.append(f"127.0.0.1:{port}")


def main():
    configure_runserver_port()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
