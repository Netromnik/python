# -*- coding: utf-8 -*-

from irk.utils.files.storage.default import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    """Файловый бэкенд, перезаписывающий файл, если он уже существует

    http://www.djangosnippets.org/snippets/976/
    http://code.djangoproject.com/ticket/4339
    http://code.djangoproject.com/ticket/11663
    """

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name
