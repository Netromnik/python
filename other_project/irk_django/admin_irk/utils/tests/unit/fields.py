# -*- coding: utf-8 -*-
import pytest
from django.db import models
from django.forms.utils import ValidationError

from irk.utils.fields.file import ExtFileField


class TestExtFileField(object):

    def test_clean(self):
        field = ExtFileField(allow=['png', 'jpg'])
        class TestModel(models.Model): pass
        model = TestModel()

        from django.core.files.base import ContentFile
        from django.db.models.fields.files import FieldFile

        with pytest.raises(ValidationError):
            # выдает исключение
            f = FieldFile(ContentFile(''), field, 'somename.exe')
            field.clean(f, model)

        with pytest.raises(ValidationError):
            # файл начинается с точки
            f = FieldFile(ContentFile(''), field, '.exe')
            field.clean(f, model)

        with pytest.raises(ValidationError):
            # файл с точкой вместо имени
            f = FieldFile(ContentFile(''), field, '.')
            field.clean(f, model)

        with pytest.raises(ValidationError):
            # файл без имени вообще
            f = FieldFile(ContentFile(''), field, '')
            field.clean(f, model)

        # проходит
        f = FieldFile(ContentFile(b'these are bytes'), field, 'somename.jpg')
        field.clean(f, model)

        # регистр любой
        f = FieldFile(ContentFile(b'these are bytes'), field, 'somename.JPG')
        field.clean(f, model)

    def test_another(self):
        try:
            field = ExtFileField('Привет')
        except KeyError:
            pass
        else:
            assert 0, 'Параметр allow должен быть обязательным'
