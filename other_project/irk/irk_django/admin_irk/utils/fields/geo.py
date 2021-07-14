# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import re

from django.contrib.gis.forms.fields import PointField
from django.contrib.gis.geos import GEOSGeometry
from django.forms.widgets import TextInput
from django.forms import ValidationError


class PointCharField(PointField):
    """Поле формы для координат с заполнением текстом"""
    widget = TextInput

    def to_python(self, value):
        """
        Преобразует входящие от пользователя данные вида lon, lat
        в строку, которую принимает на вход GEOSGeometry
        """
        if value in self.empty_values:
            return None

        if not isinstance(value, GEOSGeometry):
            value = value.strip()
            try:
                lon, lat = re.split(r',\s+|,|\s+', value)
                lon, lat = float(lon), float(lat)
            except ValueError as err:
                raise ValidationError('Неверное значение координаты')

            value = 'SRID=4326;POINT({} {})'.format(lon, lat)

        value = super(PointCharField, self).to_python(value)

        return value

    def prepare_value(self, value):
        if isinstance(value, GEOSGeometry):
            return '{}, {}'.format(value.x, value.y)
        return value
