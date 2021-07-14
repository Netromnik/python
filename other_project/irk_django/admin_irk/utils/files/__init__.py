# -*- coding: utf-8 -*-

# TODO: docstring

import uuid

from django.core.files.uploadhandler import MemoryFileUploadHandler, TemporaryFileUploadHandler


def generate_file_name(request, file_name):
    # TODO: docstring
    name = uuid.uuid4()
    return '%s.%s' % (name, file_name.split('.').pop().lower())


class MemoryUpload(MemoryFileUploadHandler):
    # TODO: docstring

    old_name = None  # TODO: зачем сделан, как class attribute?

    def new_file(self, file_name, name, *args, **kwargs):
        self.old_name = name
        name = generate_file_name(self.request, name)
        super(MemoryUpload, self).new_file(file_name, name, *args, **kwargs)

    def file_complete(self, file_size):
        file = super(MemoryUpload, self).file_complete(file_size)
        if file:
            setattr(file, 'old_name', self.old_name)

            return file


class TemporaryUpload(TemporaryFileUploadHandler):
    # TODO: docstring

    old_name = None  # TODO: зачем сделан как class attribute?

    def new_file(self, file_name, name, *args, **kwargs):
        self.old_name = name
        name = generate_file_name(self.request, name)
        super(TemporaryUpload, self).new_file(file_name, name, *args, **kwargs)

    def file_complete(self, file_size):
        file = super(TemporaryUpload, self).file_complete(file_size)
        setattr(file, 'old_name', self.old_name)
        return file
