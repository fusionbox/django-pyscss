import os

from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings

from django_pyscss.scss import DjangoScss


compiler = DjangoScss(scss_opts={
    # No compress so that I can compare more easily
    'compress': 0,
})


def compile_string(string):
    return compiler.compile(scss_string=string)


IMPORT_FOO = """
@import "css/foo.scss";
"""

with open(os.path.join(settings.BASE_DIR, 'testproject', 'static', 'css', 'foo.scss')) as f:
    FOO_CONTENTS = f.read()


IMPORT_APP1 = """
@import "css/app1.scss";
"""

with open(os.path.join(settings.BASE_DIR, 'testapp1', 'static', 'css', 'app1.scss')) as f:
    APP1_CONTENTS = f.read()


IMPORT_APP2 = """
@import "css/app2.scss";
"""

APP2_CONTENTS = FOO_CONTENTS + APP1_CONTENTS


class ImportTestMixin(object):
    def test_import_from_staticfiles_dirs(self):
        actual = compile_string(IMPORT_FOO)
        self.assertEqual(actual.strip(), FOO_CONTENTS.strip())

    def test_import_from_app(self):
        actual = compile_string(IMPORT_APP1)
        self.assertEqual(actual.strip(), APP1_CONTENTS.strip())

    def test_imports_within_file(self):
        actual = compile_string(IMPORT_APP2)
        self.assertEqual(actual.strip(), APP2_CONTENTS.strip())


@override_settings(DEBUG=True)
class FindersImportTest(ImportTestMixin, TestCase):
    pass


@override_settings(DEBUG=False)
class StorageImportTest(ImportTestMixin, TestCase):
    pass
