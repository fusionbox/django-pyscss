from __future__ import absolute_import, unicode_literals

import os

from itertools import product
from pathlib import PurePath

from scss.extension.core import CoreExtension
from scss.source import SourceFile

from ..utils import get_file_and_storage


class DjangoExtension(CoreExtension):
    name = 'django'

    def handle_import(self, name, compilation, rule):
        """
        Re-implementation of the core Sass import mechanism, which looks for
        files using the staticfiles storage and staticfiles finders.
        """
        original_path = PurePath(name)

        search_exts = list(compilation.compiler.dynamic_extensions)
        if original_path.suffix and original_path.suffix in search_exts:
            basename = original_path.stem
        else:
            basename = original_path.name

        if original_path.is_absolute():
            # Remove the beginning slash
            search_path = original_path.relative_to('/').parent
        elif rule.source_file.origin:
            search_path = rule.source_file.origin
            if original_path.parent:
                search_path = os.path.normpath(str(search_path / original_path.parent))
        else:
            search_path = original_path.parent

        for prefix, suffix in product(('_', ''), search_exts):
            filename = PurePath(prefix + basename + suffix)

            full_filename, storage = get_file_and_storage(str(search_path / filename))

            if full_filename:
                with storage.open(full_filename) as f:
                    return SourceFile.from_file(f, origin=search_path, relpath=filename)
