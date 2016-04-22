#!/usr/bin/env python
# encoding=utf-8
from __future__ import print_function
import os
import sys

if __name__ == "__main__":
    if not any([arg.startswith('--settings=') for arg in sys.argv]):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imam.devel_settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
