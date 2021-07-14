# -*- coding: UTF-8 -*-

import os

from django import template
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.conf import settings
from django.forms import Textarea

files_icons_dir = settings.BASE_PATH + '/media/img/file_icons/'
file_icons = None
for root, dirs, files in os.walk(files_icons_dir):
    file_icons = [(file.split(".")[0], file) for file in files]

register = template.Library()


@register.inclusion_tag('snippets/form_field.html')
def form_field(field, class_field=None, class_label=None, error_show=True):
    # TODO: docstring
    try:
        if error_show == '0':
            error_show = False
        else:
            error_show = True
        req = field.field.required

        if hasattr(field.field, 'max_length') and field.field.max_length > 255:
            field.field.widget = Textarea()  # TODO: Textarea не объявлен

        value = field.form.initial[field.name]

        try:
            value.file
            setattr(value, 'is_file', type(value) is FieldFile)
            if value.is_file:
                fname = value.name.split("/").pop()
                setattr(value, 'fname', fname)
                file_icon = ''
                for icon in file_icons:
                    if icon[0] == fname.split(".").pop():
                        file_icon = icon[1]
                if not file_icon:
                    file_icon = 'txt.gif'

                setattr(value, 'icon', file_icon)
            setattr(value, 'is_image', type(value) is ImageFieldFile)
        except:
            pass
    except:
        value = None

    return {'field': field,
            'class_field': class_field,
            'class_label': class_label,
            'error_show': error_show,
            'required': req,
            'value': value
    }
