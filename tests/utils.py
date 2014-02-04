from django.test import TestCase
from django.core.management import call_command


class CollectStaticTestCase(TestCase):
    def setUp(self):
        call_command('collectstatic', interactive=False)
        super(CollectStaticTestCase, self).setUp()


def clean_css(string):
    # The output of the compiled CSS doesn't have a newline between the ; and
    # the } for some reason.
    return string.strip() \
        .replace('\n', '') \
        .replace('; ', ';')
