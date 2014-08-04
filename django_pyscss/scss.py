from __future__ import absolute_import, unicode_literals

import os
from itertools import product

from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from scss import (
    Scss, dequote, log, SourceFile, SassRule, config,
)

from django_pyscss.utils import find_all_files


# TODO: It's really gross to modify this global settings variable.
# This is where PyScss is supposed to find the image files for making sprites.
config.STATIC_ROOT = find_all_files
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
    supported_extensions = ['.scss', '.sass', '.css']

    def get_file_from_storage(self, filename):
        try:
            filename = staticfiles_storage.path(filename)
        except NotImplementedError:
            # remote storages don't implement path
            pass
        if staticfiles_storage.exists(filename):
            return filename, staticfiles_storage
        else:
            return None, None

    def get_file_from_finders(self, filename):
        for file_and_storage in find_all_files(filename):
            return file_and_storage
        return None, None

    def get_file_and_storage(self, filename):
        # TODO: the switch probably shouldn't be on DEBUG
        if settings.DEBUG:
            return self.get_file_from_finders(filename)
        else:
            return self.get_file_from_storage(filename)

    def get_possible_import_paths(self, path, relative_to=None):
        """
        Returns an iterable of possible paths for an import.

        relative_to is None in the case that the SCSS is being rendered from a
        string or if it is the first file.
        """
        paths = []

        if path.startswith('/'):  # absolute import
            path = path[1:]
        elif relative_to:  # relative import
            path = os.path.join(relative_to, path)

        dirname, filename = os.path.split(path)
        name, ext = os.path.splitext(filename)
        if ext:
            search_exts = [ext]
        else:
            search_exts = self.supported_extensions
        for prefix, suffix in product(('_', ''), search_exts):
            paths.append(os.path.join(dirname, prefix + name + suffix))
        paths.append(path)
        return paths

    def _find_source_file(self, filename, relative_to=None):
        paths = self.get_possible_import_paths(filename, relative_to)
        log.debug('Searching for %s in %s', filename, paths)
        for name in paths:
            full_filename, storage = self.get_file_and_storage(name)
            if full_filename:
                if full_filename not in self.source_file_index:
                    with storage.open(full_filename) as f:
                        source = f.read()

                    source_file = SourceFile(
                        full_filename,
                        source,
                    )
                    # SourceFile.__init__ calls os.path.realpath on this, we don't want
                    # that, we want them to remain relative.
                    source_file.parent_dir = os.path.dirname(name)
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

            relative_to = rule.source_file.parent_dir
            source_file = self._find_source_file(name, relative_to)

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

    def Compilation(self, scss_string=None, scss_file=None, super_selector=None,
                    filename=None, is_sass=None, line_numbers=True,
                    relative_to=None):
        """
        Overwritten to call _find_source_file instead of
        SourceFile.from_filename.  Also added the relative_to option.
        """
        if not os.path.exists(config.ASSETS_ROOT):
            os.makedirs(config.ASSETS_ROOT)
        if super_selector:
            self.super_selector = super_selector + ' '
        self.reset()

        source_file = None
        if scss_string is not None:
            source_file = SourceFile.from_string(scss_string, filename, is_sass, line_numbers)
            # Set the parent_dir to be something meaningful instead of the
            # current working directory, which is never correct for DjangoScss.
            source_file.parent_dir = relative_to
        elif scss_file is not None:
            # Call _find_source_file instead of SourceFile.from_filename
            source_file = self._find_source_file(scss_file)

        if source_file is not None:
            # Clear the existing list of files
            self.source_files = []
            self.source_file_index = dict()

            self.source_files.append(source_file)
            self.source_file_index[source_file.filename] = source_file

        # this will compile and manage rule: child objects inside of a node
        self.parse_children()

        # this will manage @extends
        self.apply_extends()

        rules_by_file, css_files = self.parse_properties()

        all_rules = 0
        all_selectors = 0
        exceeded = ''
        final_cont = ''
        files = len(css_files)
        for source_file in css_files:
            rules = rules_by_file[source_file]
            fcont, total_rules, total_selectors = self.create_css(rules)
            all_rules += total_rules
            all_selectors += total_selectors
            if not exceeded and all_selectors > 4095:
                exceeded = " (IE exceeded!)"
                log.error("Maximum number of supported selectors in Internet Explorer (4095) exceeded!")
            if files > 1 and self.scss_opts.get('debug_info', False):
                if source_file.is_string:
                    final_cont += "/* %s %s generated add up to a total of %s %s accumulated%s */\n" % (
                        total_selectors,
                        'selector' if total_selectors == 1 else 'selectors',
                        all_selectors,
                        'selector' if all_selectors == 1 else 'selectors',
                        exceeded)
                else:
                    final_cont += "/* %s %s generated from '%s' add up to a total of %s %s accumulated%s */\n" % (
                        total_selectors,
                        'selector' if total_selectors == 1 else 'selectors',
                        source_file.filename,
                        all_selectors,
                        'selector' if all_selectors == 1 else 'selectors',
                        exceeded)
            final_cont += fcont

        return final_cont
