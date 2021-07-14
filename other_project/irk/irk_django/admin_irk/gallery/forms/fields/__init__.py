# -*- coding: utf-8 -*-

import os.path
import types

from PIL import Image
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms.widgets import ClearableFileInput
from django.template.loader import render_to_string
from sorl.thumbnail.base import ThumbnailException

from irk.gallery import models as gallery_models

ALLOWED_IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif', 'bmp')


class PictureWidget(forms.MultiWidget):
    def __init__(self, queryset, template=None, *args, **kwargs):
        self.queryset = queryset
        self.template = template
        self.image_object = None

        widgets = []
        for field in [forms.FileField(required=False),
                      forms.ModelChoiceField(queryset=gallery_models.Picture.objects.all(), widget=forms.HiddenInput),
                      forms.CharField(widget=forms.TextInput(attrs={})), forms.BooleanField(required=False)]:
            widgets.append(field.widget)
        super(PictureWidget, self).__init__(widgets)

    def decompress(self, value):
        if isinstance(value, (types.IntType, types.LongType)):
            self.image_object = self.queryset.get(pk=value)
            return [None, value, self.image_object.title, self.image_object.watermark]
        return [None, None, None, None]

    def render(self, name, value, attrs=None, renderer=None):
        if not isinstance(value, list):
            value = self.decompress(value)
        else:
            try:
                self.image_object = self.queryset.get(pk=int(value[1]))
            except (ValueError, TypeError, ObjectDoesNotExist):
                self.image_object = None
        final_attrs = self.build_attrs(attrs)

        id_ = final_attrs.get('id', None)

        fields = []
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None

            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))

                if isinstance(widget, ClearableFileInput):
                    final_attrs['data-has-value'] = 1 if value[1] else 0

                fields.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
        value = self.image_object
        context = {
            'fields': fields,
            'value': value,
        }
        return render_to_string(self.template or 'widgets/picture_field.html', context)


class Picture(forms.MultiValueField):
    widget = PictureWidget

    def __init__(self, template=None, *args, **kwargs):
        queryset = gallery_models.Picture.objects.all()
        self.widget = self.widget(queryset=queryset, template=template)
        fields = [
            forms.FileField(required=False),
            forms.ModelChoiceField(queryset=gallery_models.Picture.objects.all(), widget=forms.HiddenInput),
            forms.CharField(),
            forms.BooleanField(required=False)
        ]
        super(Picture, self).__init__(fields, *args, **kwargs)

    def widget_attrs(self, widget):
        pass

    def clean(self, value):
        """
        Validates every value in the given list. A value is validated against
        the corresponding Field in self.fields.

        For example, if this MultiValueField was instantiated with
        fields=(DateField(), TimeField()), clean() would call
        DateField.clean(value[0]) and TimeField.clean(value[1]).
        """
        clean_data = []
        errors = forms.utils.ErrorList()

        if not value or isinstance(value, (list, tuple)):
            if not value or not [v for v in value if v not in forms.fields.EMPTY_VALUES]:
                if self.required:
                    raise forms.utils.ValidationError(self.error_messages['required'])
                else:
                    return self.compress([])
        else:
            raise forms.utils.ValidationError(self.error_messages['invalid'])

        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except IndexError:
                field_value = None

            try:
                clean_data.append(field.clean(field_value))
            except forms.utils.ValidationError, e:
                # Collect all validation errors in a single list, which we'll
                # raise at the end of clean(), rather than raising a single
                # exception for the first error we encounter.
                errors.extend(e.messages)
        if errors:
            raise forms.utils.ValidationError(errors)

        if clean_data[0]:
            try:
                f = clean_data[0].file
                f.seek(0)
                img = Image.open(f)
                img.load()
                del img
                del f
            except IOError:
                raise forms.ValidationError(u'Ошибочный файл')

            extension = os.path.splitext(clean_data[0].name)[1].strip('.')
            if not extension in ALLOWED_IMAGE_EXTENSIONS:
                raise forms.ValidationError(u'Неправильный тип файла')
            picture = gallery_models.Picture(image=clean_data[0], title=clean_data[2])
        else:
            picture = clean_data[1]
            if not picture:
                raise forms.utils.ValidationError(self.error_messages['invalid'])
            picture.title = clean_data[2]

        picture.watermark = clean_data[3]

        try:
            picture.save()
        except ThumbnailException:
            raise forms.ValidationError(u'Неправильный тип файла')

        return picture
