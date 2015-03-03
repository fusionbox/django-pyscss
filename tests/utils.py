import shutil

from django.test import TestCase
from django.core.management import call_command
from django.conf import settings


class CollectStaticTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(CollectStaticTestCase, cls).setUpClass()
        call_command('collectstatic', interactive=False, verbosity=0)


class NoCollectStaticTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(NoCollectStaticTestCase, cls).setUpClass()
        shutil.rmtree(settings.STATIC_ROOT, ignore_errors=True)


def clean_css(string):
    # The output of the compiled CSS doesn't have a newline between the ; and
    # the } for some reason.
    return string.strip() \
        .replace('\n', '') \
        .replace('; ', ';')
