from __future__ import absolute_import

import os
from pathlib import PurePath

from django.utils.six.moves import StringIO

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

from scss import Compiler, config
from scss.extension.compass import CompassExtension
from scss.source import SourceFile

from .extension.django import DjangoExtension
from .utils import find_all_files, get_file_and_storage


# TODO: It's really gross to modify this global settings variable.
# This is where PyScss is supposed to find the image files for making sprites.
config.STATIC_ROOT = find_all_files
config.STATIC_URL = staticfiles_storage.url('scss/')

# This is where PyScss places the sprite files.
config.ASSETS_ROOT = os.path.join(settings.STATIC_ROOT, 'scss', 'assets')
# PyScss expects a trailing slash.
config.ASSETS_URL = staticfiles_storage.url('scss/assets/')


class DjangoScssCompiler(Compiler):
    def __init__(self, **kwargs):
        kwargs.setdefault('extensions', (DjangoExtension, CompassExtension))
        if not os.path.exists(config.ASSETS_ROOT):
            os.makedirs(config.ASSETS_ROOT)
        super(DjangoScssCompiler, self).__init__(**kwargs)

    def compile(self, *paths):
        compilation = self.make_compilation()
        for path in paths:
            path = PurePath(path)
            if path.is_absolute():
                path = path.relative_to('/')
            filename, storage = get_file_and_storage(str(path))
            with storage.open(filename) as f:
                source = SourceFile.from_file(f, origin=path.parent, relpath=PurePath(path.name))
            compilation.add_source(source)
        return self.call_and_catch_errors(compilation.run)

    def compile_string(self, string, filename=None):
        compilation = self.make_compilation()
        if filename is not None:
            f = StringIO(string)
            filename = PurePath(filename)
            source = SourceFile.from_file(f, origin=filename.parent, relpath=PurePath(filename.name))
        else:
            source = SourceFile.from_string(string)
        compilation.add_source(source)
        return self.call_and_catch_errors(compilation.run)
