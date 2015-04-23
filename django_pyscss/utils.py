import fnmatch
import os

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage


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


def get_file_from_storage(filename):
    try:
        filename = staticfiles_storage.path(filename)
    except NotImplementedError:
        # remote storages don't implement path
        pass
    if staticfiles_storage.exists(filename):
        return filename, staticfiles_storage
    else:
        return None, None


def get_file_from_finders(filename):
    for file_and_storage in find_all_files(filename):
        return file_and_storage
    return None, None


def get_file_and_storage(filename):
    name, storage = get_file_from_finders(filename)
    # get_file_from_finders could fail in production if code is a deployed as a
    # package without it's package_data. In that case, we'd assume that
    # collectstatic had been run and we can get the file from storage.
    if storage is None:
        name, storage = get_file_from_storage(filename)
    return name, storage
