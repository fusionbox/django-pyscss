from __future__ import absolute_import, unicode_literals

import os
from pathlib import Path

from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from scss import Scss
from scss.compiler import Compiler
import scss.config as config
from scss.extension.bootstrap import BootstrapExtension
from scss.extension.core import CoreExtension
from scss.extension.compass import CompassExtension
from scss.extension.extra import ExtraExtension
from scss.extension.fonts import FontsExtension

from django_pyscss.utils import find_all_files
from django.contrib.staticfiles import finders


# TODO: It's really gross to modify this global settings variable.
# This is where PyScss is supposed to find the image files for making sprites.
config.STATIC_ROOT = find_all_files
config.STATIC_URL = staticfiles_storage.url('scss/')

# This is where PyScss places the sprite files.
config.ASSETS_ROOT = os.path.join(settings.STATIC_ROOT, 'scss', 'assets')
# PyScss expects a trailing slash.
config.ASSETS_URL = staticfiles_storage.url('scss/assets/')


class DjangoOrigin(object):
    def __init__(self, path=Path()):
        self.path = path

    def __str__(self):
        me = "[django.contrib.staticfiles]"
        if self.path == Path():
            return me
        else:
            return me + "/" + str(self.path)

    def __div__(self, other):
        return DjangoOrigin(self.path / other)

    __truediv__ = __div__

    @property
    def realpath(self):
        # TODO this seems like it should use Storage, but the only way to get a
        # Storage out of the finders module is to use list(), which iterates
        # over every single file needlessly.
        # TODO this doesn't limit itself to only the staticfiles finder in
        # non-debug mode
        found = finders.find(str(self.path))
        if found:
            return Path(found)
        else:
            return None

    def is_absolute(self):
        return True

    def exists(self):
        return bool(self.realpath)

    def open(self, *args):
        if self.realpath:
            return self.realpath.open(*args)
        else:
            raise IOError


def make_django_scss_compiler(**kwargs):
    """Create a :class:`scss.Compiler` that uses the storage API for finding
    files.
    """
    # Load all the built-in extensions by default
    kwargs.setdefault('extensions', [
        CoreExtension,
        ExtraExtension,
        FontsExtension,
        CompassExtension,
        BootstrapExtension,
    ])

    # Add the Django loader to the search path
    kwargs.setdefault('search_path', []).append(DjangoOrigin())

    # Make @import work on .css files, rather than leaving them be
    kwargs.setdefault('import_static_css', True)

    return Compiler(**kwargs)


class DjangoScss(Scss):
    """
    A subclass of the Scss compiler that uses the storages API for accessing
    files.

    DEPRECATED; use :func:`make_django_scss_compiler` instead.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('search_paths', []).append(DjangoOrigin())
        super(DjangoScss, self).__init__(*args, **kwargs)

    def compile(self, *args, **kwargs):
        kwargs.setdefault('import_static_css', True)
        return super(DjangoScss, self).compile(*args, **kwargs)
