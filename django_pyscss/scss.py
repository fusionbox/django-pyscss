from __future__ import absolute_import, unicode_literals

import fnmatch

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from scss import (
    Scss, dequote, log, spawn_rule,
    OPTIONS, PROPERTIES,
)


def find_all_files(glob):
    """
    Finds all files in the django finders for a given glob,
    returns the file path, if available, and the django storage object.
    storage objects must implement the File storage API:
    https://docs.djangoproject.com/en/dev/ref/files/storage/
    """
    for finder in finders.get_finders():
        for path, storage in finder.list([]):
            if fnmatch.fnmatchcase(path, glob):
                yield path, storage


def find_one_file(path):
    for file in find_all_files(path):
        return file


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
        finally:
            with staticfiles_storage.open(filename) as f:
                return f.read()

    def get_file_from_finders(self, filename):
        path, storage = find_one_file(filename)
        with storage.open(path) as f:
            return f.read()

    def get_file_contents(self, filename):
        # TODO: the switch probably shouldn't be on DEBUG
        if settings.DEBUG:
            return self.get_file_from_finders(filename)
        else:
            return self.get_file_from_storage(filename)

    def _do_import(self, rule, p_selectors, p_parents, p_children, scope, media, c_lineno, c_property, c_codestr, code, name):
        """
        Implements @import using the django storages API.
        """
        # Protect against going to prohibited places...
        if '..' in name or '://' in name or 'url(' in name:
            rule[PROPERTIES].append((c_lineno, c_property, None))
            return

        full_filename = None
        i_codestr = None
        names = name.split(',')
        for filename in names:
            filename = dequote(name.strip())
            if '@import ' + filename in rule[OPTIONS]:
                # If already imported in this scope, skip
                continue

            try:
                i_codestr = self.scss_files[filename]
            except KeyError:
                i_codestr = self.get_file_contents(filename)

                if i_codestr is None:
                    i_codestr = self._do_magic_import(rule, p_selectors, p_parents, p_children, scope, media, c_lineno, c_property, c_codestr, code, name)
                    if i_codestr is None:
                        log.warn("I couldn't find this file (%s)." % filename)

                i_codestr = self.scss_files[name] = i_codestr and self.load_string(i_codestr, full_filename)
                if name not in self.scss_files:
                    self._scss_files_order.append(name)
            if i_codestr is not None:
                _rule = spawn_rule(rule, codestr=i_codestr, path=full_filename, lineno=c_lineno)
                self.manage_children(_rule, p_selectors, p_parents, p_children, scope, media)
                rule[OPTIONS]['@import ' + name] = True
