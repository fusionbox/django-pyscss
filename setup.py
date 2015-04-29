#!/usr/bin/env python
from setuptools import setup, find_packages
import os

__doc__ = "Makes it easier to use PySCSS in Django."


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires = [
    'Django>=1.4',
    'pyScss>=1.3.4',
]

try:
    import pathlib
except ImportError:
    install_requires.append('pathlib')

tests_require = [
    'Pillow',
    'django-compressor>=1.3',
    'django-discover-runner',
    'mock',
]


version = '2.0.2'


setup(
    name='django-pyscss',
    version=version,
    author="Fusionbox, Inc.",
    author_email="programmers@fusionbox.com",
    url="https://github.com/fusionbox/django-pyscss",
    keywords="django css scss sass pyscss compressor",
    description=__doc__,
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    packages=[package for package in find_packages() if package.startswith('django_pyscss')],
    install_requires=install_requires,
    tests_require=tests_require,
    zip_safe=False,
    include_package_data=True,
    test_suite='testproject.runtests.runtests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
