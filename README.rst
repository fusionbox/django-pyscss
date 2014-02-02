django-pyscss
-------------

A collection of tools for making it easier to use PyScss within Django.

.. class:: django_pyscss.scss.DjangoScss

    A subclass of :class:`scss.Scss` that uses the Django staticfiles storage
    and finders instead of the filesystem.  This obseletes the load_paths
    option that was present previously by searching instead in your staticfiles
    directories.

    In DEBUG mode, DjangoScss will search using all of the finders to find the
    file.  If you are not in DEBUG mode, it assumes you have run collectstatic
    and will only use staticfiles_storage to find the file.


Running the tests
=================

You first have to run `./manage.py collectstatic` before you can run the tests
for the first time.  After that, you can just run::

    $ python setup.py test
