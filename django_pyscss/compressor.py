from __future__ import absolute_import

import os

from compressor.filters import FilterBase
from compressor.conf import settings

from django_pyscss.scss import DjangoScss


class DjangoScssFilter(FilterBase):
    compiler = DjangoScss()

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
            self.relative_to = None
        else:
            self.relative_to = os.path.dirname(href.replace(settings.STATIC_URL, ''))

    def input(self, **kwargs):
        return self.compiler.compile(scss_string=self.content,
                                     relative_to=self.relative_to)
