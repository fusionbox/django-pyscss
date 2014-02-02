import os

from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings

from django_pyscss.scss import DjangoScss

from tests.utils import clean_css


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
        self.assertEqual(clean_css(actual), clean_css(FOO_CONTENTS))

    def test_import_from_app(self):
        actual = compile_string(IMPORT_APP1)
        self.assertEqual(clean_css(actual), clean_css(APP1_CONTENTS))

    def test_imports_within_file(self):
        actual = compile_string(IMPORT_APP2)
        self.assertEqual(clean_css(actual), clean_css(APP2_CONTENTS))


@override_settings(DEBUG=True)
class FindersImportTest(ImportTestMixin, TestCase):
    pass


@override_settings(DEBUG=False)
class StorageImportTest(ImportTestMixin, TestCase):
    pass


INLINE_IMAGE = """
.loading {
  background: inline_image('images/loading.gif') center no-repeat;
}
"""

INLINED_IMAGE_EXPECTED = """
.loading {
  background: url(data:image/gif;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABs0lEQVR4nKXTzUojQRDA8X9/zJCIECRfiDCDBHKZq+QR8nJ5Hl/AQ2QgxyCOoCAy8eIkAxLy0dPWnkzQ7JpdtqAv3fSP6qouJSL8T9jvGy8vLzKdTsmyjDzPGY1G6q+B29tbubm5YTab4b3n4+Njd1ZVlYgIWmuMMeoASNNUrq+vWa/XDAYDkiTh8vJyByil8N7jnCMMQ7HWqh2Q57mMx2OccwyHQ4bD4UHaxhglIuKcY71eU6/XxRijNMDDwwNFUXB1dfXby7t0rVVaa5xzbDYbADTA8/MzWmuSJPmpXp8IVVXtAAtQFAVBEBBF0VEgDENVVZV47/eA1hprLUr92DEAvPfinENrvX/C+fk5QRAwm82OAqvVCuccxpg9EMcxxhienp6OAmVZst1uCcNwD/R6PbrdLo+Pj0wmkz/+7dfXV3l7e8Nay8nJCQDqcxbu7u4kTVNEhH6/TxzHdDodlFKUZclisWA+n1Or1YiiiGazqb4AAPf395JlGe/v71hrCcPwy2o0GlxcXNDpdHbVVt+ncT6fS57nFEXBcrkkCALOzs5otVq0221OT0+/tOoA+Nf4BawEx9v4UlbsAAAAAElFTkSuQmCC) center no-repeat;
}
"""

SPRITE_MAP = """
$widgets: sprite-map('images/icons/widget-*.png');

.foo {
  background: sprite($widgets, 'widget-skull-and-crossbones');
}

.bar {
  background: sprite($widgets, 'widget-google-map');
}
"""


class AssetsTest(TestCase):
    def test_inline_image(self):
        actual = compile_string(INLINE_IMAGE)
        self.assertEqual(clean_css(actual), clean_css(INLINED_IMAGE_EXPECTED))

    def test_sprite_images(self):
        actual = compile_string(SPRITE_MAP)
        # pyScss puts a cachebuster query string on the end of the URLs, lets
        # just check that it made the file that we expected.
        self.assertIn('KUZdBAnPCdlG5qfocw9GYw.png', actual)
