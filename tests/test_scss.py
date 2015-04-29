import os
import re
import mock

from django.test import TestCase
from django.conf import settings

from scss.errors import SassImportError

from django_pyscss import DjangoScssCompiler

from tests.utils import clean_css, CollectStaticTestCase, NoCollectStaticTestCase


with open(os.path.join(settings.BASE_DIR, 'testproject', 'static', 'css', 'foo.scss')) as f:
    FOO_CONTENTS = f.read()

with open(os.path.join(settings.BASE_DIR, 'testapp1', 'static', 'css', 'app1.scss')) as f:
    APP1_CONTENTS = f.read()

APP2_CONTENTS = FOO_CONTENTS + APP1_CONTENTS

SASS_CONTENTS = """
.sass {
  color: #009900;
}
"""

with open(os.path.join(settings.BASE_DIR, 'testproject', 'static', 'css', 'css_file.css')) as f:
    CSS_CONTENTS = f.read()

with open(os.path.join(settings.BASE_DIR, 'testproject', 'static', 'css', '_baz.scss')) as f:
    BAZ_CONTENTS = f.read()

with open(os.path.join(settings.BASE_DIR, 'testproject', 'static', 'css', 'sub', '_spam.scss')) as f:
    SPAM_CONTENTS = f.read()

BAZ_CONTENTS = BAZ_CONTENTS.replace('@import "sub/spam";', SPAM_CONTENTS)

with open(os.path.join(settings.BASE_DIR, 'testproject', 'static', 'css', 'path_conflict.scss')) as f:
    PATH_CONFLICT_CONTENTS = f.read()


class CompilerTestMixin(object):
    def setUp(self):
        self.compiler = DjangoScssCompiler()
        super(CompilerTestMixin, self).setUp()


class ImportTestMixin(CompilerTestMixin):
    def test_import_from_staticfiles_dirs(self):
        actual = self.compiler.compile_string('@import "/css/foo.scss";')
        self.assertEqual(clean_css(actual), clean_css(FOO_CONTENTS))

    def test_import_from_staticfiles_dirs_prefixed(self):
        actual = self.compiler.compile_string('@import "/css_prefix/baz.scss";')
        self.assertEqual(clean_css(actual), clean_css(FOO_CONTENTS))

    def test_import_from_staticfiles_dirs_relative(self):
        actual = self.compiler.compile_string('@import "css/foo.scss";')
        self.assertEqual(clean_css(actual), clean_css(FOO_CONTENTS))

    def test_import_from_app(self):
        actual = self.compiler.compile_string('@import "/css/app1.scss";')
        self.assertEqual(clean_css(actual), clean_css(APP1_CONTENTS))

    def test_import_from_app_relative(self):
        actual = self.compiler.compile_string('@import "css/app1.scss";')
        self.assertEqual(clean_css(actual), clean_css(APP1_CONTENTS))

    def test_imports_within_file(self):
        actual = self.compiler.compile_string('@import "/css/app2.scss";')
        self.assertEqual(clean_css(actual), clean_css(APP2_CONTENTS))

    def test_relative_import(self):
        actual = self.compiler.compile('/css/bar.scss')
        self.assertEqual(clean_css(actual), clean_css(FOO_CONTENTS))

    def test_relative_import_with_filename(self):
        actual = self.compiler.compile_string('@import "foo.scss";', 'css/bar.scss')
        self.assertEqual(clean_css(actual), clean_css(FOO_CONTENTS))

    def test_bad_import(self):
        self.assertRaises(SassImportError, self.compiler.compile_string, '@import "this-file-does-not-and-should-never-exist.scss";')

    def test_no_extension_import(self):
        actual = self.compiler.compile_string('@import "/css/foo";')
        self.assertEqual(clean_css(actual), clean_css(FOO_CONTENTS))

    def test_no_extension_import_sass(self):
        actual = self.compiler.compile_string('@import "/css/sass_file";')
        self.assertEqual(clean_css(actual), clean_css(SASS_CONTENTS))

    # def test_no_extension_import_css(self):
    #     actual = self.compiler.compile_string('@import "/css/css_file";')
    #     self.assertEqual(clean_css(actual), clean_css(CSS_CONTENTS))

    def test_import_underscore_file(self):
        actual = self.compiler.compile_string('@import "/css/baz";')
        self.assertEqual(clean_css(actual), clean_css(BAZ_CONTENTS))

    def test_import_conflict(self):
        actual = self.compiler.compile_string('@import "/css/path_conflict";')
        self.assertEqual(clean_css(actual), clean_css(PATH_CONFLICT_CONTENTS))


class FindersImportTest(ImportTestMixin, NoCollectStaticTestCase):
    pass


# Emulate the condition where collectstatic was run but the source files are no
# longer available.
@mock.patch('django_pyscss.utils.get_file_from_finders',
            new=mock.MagicMock(return_value=(None, None)))
class StorageImportTest(ImportTestMixin, CollectStaticTestCase):
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


class AssetsTest(CompilerTestMixin, TestCase):
    def test_inline_image(self):
        actual = self.compiler.compile_string(INLINE_IMAGE)
        self.assertEqual(clean_css(actual), clean_css(INLINED_IMAGE_EXPECTED))

    def test_sprite_images(self):
        actual = self.compiler.compile_string(SPRITE_MAP)
        # pyScss puts a cachebuster query string on the end of the URLs, lets
        # just check that it made the file that we expected.
        self.assertTrue(re.search(r'url\(/static/scss/assets/images_icons-.+\.png\?_=\d+', actual))
