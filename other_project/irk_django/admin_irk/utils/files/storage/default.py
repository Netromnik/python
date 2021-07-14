# -*- coding: utf-8 -*-

import os
import imghdr
import logging
import subprocess

from django.conf import settings
from django.core.files.storage import FileSystemStorage as BaseStorage

from irk.utils import settings as app_settings


logger = logging.getLogger(__name__)


class FileSystemStorage(BaseStorage):

    def save(self, name, content, max_length=None):
        filename = super(FileSystemStorage, self).save(name, content, max_length)

        self._remove_exif(filename)

        return filename

    def _remove_exif(self, filename):
        """Удаляем exif из изображений после их загрузки"""

        absolute_path = os.path.join(settings.MEDIA_ROOT, filename)

        if imghdr.what(absolute_path) != 'jpeg':
            logger.debug('File `%s` is not a JPEG file. Skipping EXIF data removal'.format(absolute_path))
            return

        try:
            subprocess.call([app_settings.EXIV2_PATH, '-d', 'a', absolute_path])
        except OSError:
            logger.exception('Got a exception while removing EXIF data from image')
