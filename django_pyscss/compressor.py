from __future__ import absolute_import

import os

from compressor.filters import FilterBase

from django_pyscss.scss import DjangoScss, config


class DjangoScssFilter(FilterBase):
    compiler = DjangoScss()

    def __init__(self, content, attrs=None, filter_type=None, filename=None):
        # It looks like there is a bug in django-compressor because it expects
        # us to accept attrs.
        super(DjangoScssFilter, self).__init__(content, filter_type, filename)

    def input(self, **kwargs):
        if not os.path.exists(config.ASSETS_ROOT):
            os.makedirs(config.ASSETS_ROOT)
        return self.compiler.compile(self.content)
