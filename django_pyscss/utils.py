import fnmatch
import os

from django.contrib.staticfiles import finders


def find_all_files(glob):
    """
    Finds all files in the django finders for a given glob,
    returns the file path, if available, and the django storage object.
    storage objects must implement the File storage API:
    https://docs.djangoproject.com/en/dev/ref/files/storage/
    """
    for finder in finders.get_finders():
        for path, storage in finder.list([]):
            if fnmatch.fnmatchcase(os.path.join(getattr(storage, 'prefix', '')
                                                or '', path),
                                   glob):
                yield path, storage
