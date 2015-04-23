CHANGELOG
---------


2.0.1 (2015-04-23)
==================

- Explicitly depend on pathlib, instead of assuming pyScss will require it. [#33]
- Fixed cases where DEBUG is False but collectstatic hasn't been run (common in tests).


2.0.0 (2015-04-22)
==================

- Added support for pyScss 1.3 and Python 3.
- Dropped support for pyScss 1.2

Upgrade path
^^^^^^^^^^^^

If you are just using the django-compressor integration, you don't have to
upgrade anything.

If you were using the ``DjangoScss`` class directly, it has been replaced with
the ``DjangoScssCompiler`` class. The API for compiling CSS has changed as
well, for example, to compile from a string, previously you would do it like
this:

.. code-block:: python

    >>> from django_pyscss.scss import DjangoScss
    >>> compiler = DjangoScss()
    >>> compiler.compile(".foo { color: red; }")

Now the interface is like this:

.. code-block:: python

    >>> from django_pyscss import DjangoScssCompiler
    >>> compiler = DjangoScssCompiler()
    >>> compiler.compile_string(".foo { color: red; }")

You read more about the new API on the `pyScss API documentation
<http://pyscss.readthedocs.org/en/latest/python-api.html#new-api>`_.


1.0.0 - 2014-02-11
==================

Released django-pyscss.
