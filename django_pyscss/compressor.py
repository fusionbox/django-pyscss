from __future__ import absolute_import

from pathlib import Path

from compressor.filters import FilterBase
from compressor.conf import settings
from scss.cssdefs import determine_encoding
from scss.source import SourceFile

from django_pyscss.scss import DjangoOrigin
from django_pyscss.scss import make_django_scss_compiler


class DjangoScssFilter(FilterBase):
    compiler = make_django_scss_compiler()

    def __init__(self, content, attrs=None, filter_type=None, filename=None, **kwargs):
        # It looks like there is a bug in django-compressor because it expects
        # us to accept attrs.
        super(DjangoScssFilter, self).__init__(content, filter_type, filename, **kwargs)
        try:
            # this is a link tag which means there is an SCSS file being
            # referenced.
            href = attrs['href']
        except KeyError:
            # this is a style tag which means this is inline SCSS.
            self.origin = None
            self.relpath = None
        else:
            # All we have is a URL, which probably came from {% static %}.  So
            # chop off the STATIC_URL prefix to get the original relative path,
            # and use the Django loader.
            self.origin = DjangoOrigin()
            self.relpath = Path(href.replace(settings.STATIC_URL, ''))

    def input(self, **kwargs):
        source = SourceFile(
            self.origin, self.relpath, self.content,
            encoding=determine_encoding(self.content),
        )
        return self.compiler.compile_sources(source)
