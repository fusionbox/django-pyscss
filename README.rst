django-pyscss
-------------

A collection of tools for making it easier to use pyScss within Django.

.. image:: https://travis-ci.org/fusionbox/django-pyscss.png
   :target: http://travis-ci.org/fusionbox/django-pyscss
   :alt: Build Status

.. image:: https://coveralls.io/repos/fusionbox/django-pyscss/badge.png?branch=master
   :target: https://coveralls.io/r/fusionbox/django-pyscss
   :alt: Coverage Status

Why do we need this?
====================

This app smooths over a lot of things when dealing with pyScss in Django.  It

- Overwrites the import system to use Django's staticfiles app.  This way you
  can import SCSS files from any app (or any file that's findable by the
  STATICFILES_FINDERS) with no hassle.

- Configures pyScss to work with the staticfiles app for it's image functions
  (e.g. inline-image and sprite-map).

- It provides a django-compressor precompile filter class so that you can
  easily use pyScss with django-compressor without having to bust out to the
  shell.  This has the added benefit of removing the need to configure pyScss
  through its command-line arguments AND makes it possible for the exceptions
  and warnings that pyScss emits to bubble up to your process so that you can
  actually know what's going on.


Rendering SCSS manually
=======================

You can render SCSS manually from a string like this::

    from django_pyscss.scss import DjangoScss

    compiler = DjangoScss()
    compiler.compile(scss_string=".foo { color: green; }")

You can render SCSS from a file like this::

    from django_pyscss.scss import DjangoScss

    compiler = DjangoScss()
    compiler.compile(scss_file='css/styles.scss')

The file needs to be able to be located by staticfiles finders in order to be
used.


.. class:: django_pyscss.scss.DjangoScss

    A subclass of :class:`scss.Scss` that uses the Django staticfiles storage
    and finders instead of the filesystem.  This obsoletes the load_paths
    option that was present previously by searching instead in your staticfiles
    directories.

    In DEBUG mode, DjangoScss will search using all of the finders to find the
    file.  If you are not in DEBUG mode, it assumes you have run collectstatic
    and will only use staticfiles_storage to find the file.


Using in conjunction with django-compressor.
============================================

django-pyscss comes with support for django-compressor.  All you have to do is
add it to your ``COMPRESS_PRECOMPILERS`` setting. ::

    COMPRESS_PRECOMPILERS = (
        # ...
        ('text/x-scss', 'django_pyscss.compressor.DjangoScssFilter'),
        # ...
    )

Then you can just use SCSS like you would use CSS normally. ::

    {% compress css %}
    <link rel="stylesheet" type="text/x-scss" href="{% static 'css/styles.css' %}">
    {% endcompress %}


Running the tests
=================

You can run the tests by running.

    $ python setup.py test

Please note that this will collecstatic into ``tmp/static/`` automatically as
some of the tests require the staticfiles to have been collected.
