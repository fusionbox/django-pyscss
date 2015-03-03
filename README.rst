django-pyscss
-------------

A collection of tools for making it easier to use pyScss within Django.

.. image:: https://travis-ci.org/fusionbox/django-pyscss.png
   :target: http://travis-ci.org/fusionbox/django-pyscss
   :alt: Build Status

.. image:: https://coveralls.io/repos/fusionbox/django-pyscss/badge.png?branch=master
   :target: https://coveralls.io/r/fusionbox/django-pyscss
   :alt: Coverage Status


.. note::

    This version only supports pyScss 1.3.4 and greater. For pyScss 1.2 support,
    you can use the 1.x series of django-pyscss.


Installation
============

django-pyscss supports Django 1.4+, and Pythons 2 and 3.

You may install django-pyscss off of PyPI::

    pip install django-pyscss


Why do we need this?
====================

This app smooths over a lot of things when dealing with pyScss in Django.  It

- Overwrites the import system to use Django's staticfiles app.  This way you
  can import SCSS files from any app (or any file that's findable by the
  STATICFILES_FINDERS) with no hassle.

- Configures pyScss to work with the staticfiles app for its image functions
  (e.g. inline-image and sprite-map).

- It provides a django-compressor precompile filter class so that you can
  easily use pyScss with django-compressor without having to bust out to the
  shell.  This has the added benefit of removing the need to configure pyScss
  through its command-line arguments AND makes it possible for the exceptions
  and warnings that pyScss emits to bubble up to your process so that you can
  actually know what's going on.


Rendering SCSS manually
=======================

You can render SCSS manually from a string like this:

.. code-block:: python

    from django_pyscss import DjangoScssCompiler

    compiler = DjangoScssCompiler()
    compiler.compile_string(".foo { color: green; }")

You can render SCSS from a file like this:

.. code-block:: python

    from django_pyscss import DjangoScssCompiler

    compiler = DjangoScssCompiler()
    compiler.compile('css/styles.scss')

The file needs to be able to be located by staticfiles finders in order to be
used.

The ``DjangoScssCompiler`` class is a subclass of ``scss.Compiler`` that
injects the ``DjangoExtension``. ``DjangoExtension`` is what overrides the
import mechanism.

``DjangoScssCompiler`` also turns on the CompassExtension by default, if you
wish to turn this off you do so:

.. code-block:: python

    from django_pyscss import DjangoScssCompiler
    from django_pyscss.extensions.django import DjangoExtension

    compiler = DjangoScssCompiler(extensions=[DjangoExtension])

For a list of options that ``DjangoScssCompiler`` accepts, please see the
pyScss `API documentation <http://pyscss.readthedocs.org/en/latest/python-api.html#new-api>`_.


Using in conjunction with django-compressor
===========================================

django-pyscss comes with support for django-compressor.  All you have to do is
add it to your ``COMPRESS_PRECOMPILERS`` setting. :

.. code-block:: python

    COMPRESS_PRECOMPILERS = (
        # ...
        ('text/x-scss', 'django_pyscss.compressor.DjangoScssFilter'),
        # ...
    )

Then you can just use SCSS like you would use CSS normally. :

.. code-block:: html+django

    {% compress css %}
    <link rel="stylesheet" type="text/x-scss" href="{% static 'css/styles.css' %}">
    {% endcompress %}

If you wish to provide your own compiler instance (for example if you wanted to
change some settings on the ``DjangoScssCompiler``), you can subclass
``DjangoScssFilter``. :

.. code-block:: python

    # myproject/scss_filter.py
    from django_pyscss import DjangoScssCompiler
    from django_pyscss.compressor import DjangoScssFilter

    class MyDjangoScssFilter(DjangoScssFilter):
        compiler = DjangoScssCompiler(
            # Example configuration
            output_style='compressed',
        )

    # settings.py
    COMPRESS_PRECOMPILERS = (
        # ...
        ('text/x-scss', 'myproject.scss_filter.MyDjangoScssFilter'),
        # ...
    )


Running the tests
=================

You can run the tests by running.

    $ python setup.py test

Please note that this will collecstatic into ``tmp/static/`` automatically as
some of the tests require the staticfiles to have been collected.
