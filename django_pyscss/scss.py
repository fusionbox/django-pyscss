from __future__ import absolute_import, unicode_literals

import os

from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from scss import (
    Scss, dequote, log, SourceFile, SassRule, config,
)

from django_pyscss.utils import find_one_file


# This is where PyScss is supposed to find the image files for making sprites.
config.STATIC_ROOT = find_one_file
config.STATIC_URL = staticfiles_storage.url('scss/')

# This is where PyScss places the sprite files.
config.ASSETS_ROOT = os.path.join(settings.STATIC_ROOT, 'scss', 'assets')
# PyScss expects a trailing slash.
config.ASSETS_URL = staticfiles_storage.url('scss/assets/')


class DjangoScss(Scss):
    """
    A subclass of the Scss compiler that uses the storages API for accessing
    files.
    """
    def get_file_from_storage(self, filename):
        try:
            filename = staticfiles_storage.path(filename)
        except NotImplementedError:
            # remote storages don't implement path
            pass
        return filename, staticfiles_storage

    def get_file_from_finders(self, filename):
        return find_one_file(filename)

    def get_file_and_storage(self, filename):
        # TODO: the switch probably shouldn't be on DEBUG
        if settings.DEBUG:
            return self.get_file_from_finders(filename)
        else:
            return self.get_file_from_storage(filename)

    def _find_source_file(self, name):
        full_filename, storage = self.get_file_and_storage(name)
        if name not in self.source_files:
            with storage.open(full_filename) as f:
                source = f.read()
            source_file = SourceFile(
                full_filename,
                source,
                parent_dir=os.path.realpath(os.path.dirname(full_filename)),
            )
            self.source_files.append(source_file)
            self.source_file_index[full_filename] = source_file
        return self.source_file_index[full_filename]

    def _do_import(self, rule, scope, block):
        """
        Implements @import using the django storages API.
        """
        # Protect against going to prohibited places...
        if any(scary_token in block.argument for scary_token in ('..', '://', 'url(')):
            rule.properties.append((block.prop, None))
            return

        full_filename = None
        names = block.argument.split(',')
        for name in names:
            name = dequote(name.strip())

            source_file = self._find_source_file(name)

            if source_file is None:
                i_codestr = self._do_magic_import(rule, scope, block)

                if i_codestr is not None:
                    source_file = SourceFile.from_string(i_codestr)
                    self.source_files.append(source_file)
                    self.source_file_index[full_filename] = source_file

            if source_file is None:
                log.warn("File to import not found or unreadable: '%s' (%s)", name, rule.file_and_line)
                continue

            import_key = (name, source_file.parent_dir)
            if rule.namespace.has_import(import_key):
                # If already imported in this scope, skip
                continue

            _rule = SassRule(
                source_file=source_file,
                lineno=block.lineno,
                import_key=import_key,
                unparsed_contents=source_file.contents,

                # rule
                options=rule.options,
                properties=rule.properties,
                extends_selectors=rule.extends_selectors,
                ancestry=rule.ancestry,
                namespace=rule.namespace,
            )
            rule.namespace.add_import(import_key, rule.import_key, rule.file_and_line)
            self.manage_children(_rule, scope)
