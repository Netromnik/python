# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class FileSizeValidator(object):
    def __init__(self, max_size=None, message=None, code=None):
        self.max_size = max_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        filesize = value.size

        if filesize > self.max_size:
            raise ValidationError(u'Максимальный размер файла {}MB'.format(self.max_size / 1024 / 1024))
