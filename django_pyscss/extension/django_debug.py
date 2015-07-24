from __future__ import absolute_import

from django.conf import settings

from scss.extension import Extension
from scss.namespace import Namespace
from scss.types import Boolean


class DjangoDebugExtension(Extension):
    name = 'django_debug'

    def __init__(self):
        namespace = Namespace()
        namespace.set_variable('$debug', Boolean(settings.DEBUG))
        self.namespace = namespace
