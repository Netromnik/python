# -*- coding: utf-8 -*-

from django.core.exceptions import FieldError, ValidationError
from django.db import models


class SetField(models.Field):
    """Model Field for store set of values"""

    description = u'Поле хранящее множество значений.'

    def __init__(self, *args, **kwargs):
        self.values = kwargs.pop('values', set())
        super(SetField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        if 'mysql' in connection.settings_dict['ENGINE']:
            return u'set({})'.format(self._serialize(self.values))
        else:
            raise FieldError('SetField only supported on MySQL engine.')

    def to_python(self, value):
        if isinstance(value, set):
            return value

        if value is None:
            return value

        return self._parse(value)

    def get_prep_value(self, value):
        return self._serialize(value)

    def from_db_value(self, value, expression, connection, context):
        # Используется в Django 1.8+
        if value is None:
            return value

        return self._parse(value)

    def deconstruct(self):
        name, path, args, kwargs = super(SetField, self).deconstruct()

        kwargs['values'] = self.values

        return name, path, args, kwargs

    def _parse(self, string):
        """Разобрать строку хранящую представление множества в БД

        :param str string: строка хранящая множество значений через запятую
        """

        try:
            values = string.split(',')
        except Exception:
            raise ValidationError(u"Cant't convert {} to set".format(string))

        return set(values)

    def _serialize(self, values):
        """Закодировать множество значений в строку"""

        return u','.join(unicode(v) for v in sorted(values))
