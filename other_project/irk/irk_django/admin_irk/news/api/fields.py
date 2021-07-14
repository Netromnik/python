# -*- coding: utf-8 -*-

from rest_framework.fields import Field


class CategoryField(Field):

    def to_native(self, value):
        if value is None:
            return None

        return {
            'id': value.id,
            'title': value.title,
        }
