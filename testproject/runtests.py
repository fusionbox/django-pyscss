#!/usr/bin/env python
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.testproject.settings")

import django
if hasattr(django, 'setup'):
    django.setup()

from django.test.utils import get_runner
from django.conf import settings


def runtests():
    # Stolen from django/core/management/commands/test.py
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    # failures = test_runner.run_tests(['tests.test_scss.FindersImportTest.test_relative_import_with_filename'])
    failures = test_runner.run_tests(['tests'])
    sys.exit(bool(failures))
