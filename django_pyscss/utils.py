import fnmatch
import os
import collections

from django.contrib.staticfiles import finders


def find_all_files(glob):
    """
    Finds all files in the django finders for a given glob,
    returns the file path, if available, and the django storage object.
    storage objects must implement the File storage API:
    https://docs.djangoproject.com/en/dev/ref/files/storage/
    """
    found_files = collections.OrderedDict()
    for finder in finders.get_finders():
        for path, storage in finder.list([]):
            if getattr(storage, 'prefix', None):
                prefixed_path = os.path.join(storage.prefix, path)
            else:
                prefixed_path = path
            
            if prefixed_path not in found_files:
                found_files[prefixed_path] = (storage, path)

            if fnmatch.fnmatchcase(prefixed_path, glob):
                yield path, storage
