# -*- coding: utf-8 -*-

import zipfile

from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from adv.settings import ALLOWED_BANNER_EXTENSIONS


def validate_html5_file(archive):
    """Проверить файл, загруженный в поле html5-баннер"""
    try:
        with zipfile.ZipFile(archive) as f:
            f.open('index.html')
    except zipfile.BadZipfile:
        raise ValidationError(u'Не могу прочитать zip-архив')
    except KeyError:
        raise ValidationError(u'В корне архива должен быть файл index.html')
    return archive


validate_banner_file_extension = FileExtensionValidator(
    allowed_extensions=ALLOWED_BANNER_EXTENSIONS,
)
