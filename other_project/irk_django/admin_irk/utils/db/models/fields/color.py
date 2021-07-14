# -*- coding: utf-8 -*-

import re

from django.db import models
from django import forms
from django.utils.html import format_html

__all__ = ('ColorField', )


COLOR_RE = re.compile(r'^#?[0-9abcdef]{6}$', re.I)


class ColorWidget(forms.TextInput):

    style = u'''{}<style type="text/css">#{} {{ border-right: 10px solid #{}; }}</style>'''

    def value_from_datadict(self, data, files, name):
        return data.get(name, None)

    def render(self, name, value, attrs=None, renderer=None):
        html = super(ColorWidget, self).render(name, value, attrs, renderer)
        if value:
            html = self.style.format(html, attrs['id'], value)

        return format_html(html.replace('{', '{{').replace('}', '}}'))


class ColorFormField(forms.fields.RegexField):
    widget = ColorWidget

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'min_length': 6,
            'max_length': 7,
        })
        super(ColorFormField, self).__init__(COLOR_RE, *args, **kwargs)

    def to_python(self, value):
        value = super(ColorFormField, self).to_python(value)
        return value.lstrip('#') if value else value



class ColorField(models.CharField):
    """Поле для ввода HEX значения цвета

    В базе хранится в виде строки из шести символов, без начального «#»
    """

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'max_length': 6,
            'help_text': u'В формате #13bf99',
        })
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.update({
            'form_class': ColorFormField,
            'widget': ColorWidget,
        })

        return super(ColorField, self).formfield(**kwargs)
