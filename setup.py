#!/usr/bin/env python
from setuptools import setup, find_packages
import subprocess
import os

__doc__ = """
Makes it easier to use PySCSS in Django.
"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires = [
    'Django>=1.4',
    'PyScss>=1.2.0',
]
tests_require = [
    'Pillow',
    'django-compressor>=1.3',
    'django-discover-runner',
]


version = (0, 0, 1, 'final')


def get_version():
    number = '.'.join(map(str, version[:3]))
    stage = version[3]
    if stage == 'final':
        return number
    elif stage == 'alpha':
        process = subprocess.Popen('git rev-parse HEAD'.split(), stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return number + '-' + stdout.strip()[:8]

setup(
    name='django-pyscss',
    version=get_version(),
    description=__doc__,
    long_description=read('README.rst'),
    packages=[package for package in find_packages() if package.startswith('django_pyscss')],
    install_requires=install_requires,
    tests_require=tests_require,
    zip_safe=False,
    include_package_data=True,
    test_suite='testproject.runtests.runtests',
)
