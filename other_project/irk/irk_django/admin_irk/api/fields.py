# -*- coding: utf-8 -*-

from django.conf import settings
from rest_framework import serializers

from irk.utils.templatetags.str_utils import do_typograph


class GalleryRelatedField(serializers.RelatedField):
    """Поле для конвертирования галереи"""

    many = True

    def to_native(self, value):
        return self.process(value)

    @staticmethod
    def process(value):
        if value is None:
            return []

        images = value.pictures.all().order_by('-gallerypicture__main', 'gallerypicture__position')

        response = []
        for idx, image in enumerate(images):
            try:
                response.append({
                    'image': image.image.url,
                    'width': image.image.width,
                    'height': image.image.height,
                    'title': image.title,
                    'is_main': idx == 0,  # Метод main_gallery() возвращает список изображений с главной на первом месте
                })
            except (OSError, IOError):
                if settings.DEBUG:
                    continue
                raise

        return response


class TypographField(serializers.CharField):
    """Обработка текста поля типографом"""

    def __init__(self, rules='', *args, **kwargs):
        super(TypographField, self).__init__(*args, **kwargs)

        self.rules = rules

    def to_native(self, value):
        value = super(TypographField, self).from_native(value)

        return self.process(value)

    @staticmethod
    def process(value):
        return do_typograph(value, 'title')
