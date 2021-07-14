# -*- coding: utf-8 -*-

import json

from django import forms
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType

from irk.utils.files.admin import admin_media_static


class AjaxSuggestWidget(forms.widgets.MultiWidget):
    def __init__(self, model, fk=True, allow_non_fk=False, extra_suggest_options=None, attrs=None, *args, **kwargs):
        self.fk = fk
        self._postfix = None
        self.allow_non_fk = allow_non_fk
        if fk:
            self._postfix = '_suggest'

        # TODO: reverse
        self.url = '/utils/objects/%s/' % ContentType.objects.get_for_model(model).pk
        self.model = model
        self.extra_suggest_options = extra_suggest_options or {}

        widgets = (
            forms.widgets.HiddenInput(attrs),
            forms.widgets.TextInput(attrs),
        )

        super(AjaxSuggestWidget, self).__init__(widgets, attrs, *args, **kwargs)

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/plugins.js',)
        css = {
            'all': ('css/admin.css',),
        }

    def id_for_label(self, id_):
        return id_ + self._postfix

    def render(self, name, value, attrs=None, renderer=None):
        if self.fk and not isinstance(value, list):
            value = self.decompress(value)
        final_attrs = self.build_attrs(attrs)
        ac_options = {
            'delay': 100,
            'width': 400,
            'minChars': 1,
            'matchContains': True,
        }
        ac_options.update(self.extra_suggest_options)
        callback_name = name.replace("-", "_")
        return render_to_string('widget/AjaxSuggest.html', dict(name=name, value=value,
                                                                attrs=attrs, url=self.url, postfix=self._postfix,
                                                                ac_options=json.dumps(ac_options),
                                                                callback_name=callback_name))

    def value_from_datadict(self, data, files, name):
        try:
            if self.fk:
                id_ = int(data.get(name, None))
                obj = self.model.objects.get(pk=id_)
                return id_, unicode(obj)
            else:
                return data.get(name, None)
        except:
            if self.allow_non_fk:
                result = (None, data.get("%s%s" % (name, self._postfix)))
            else:
                result = (None, None)

            return result

    def decompress(self, data):
        try:
            if type(data) is tuple:
                value = data[0]
            else:
                value = data
            obj = self.model.objects.get(pk=value)
        except self.model.DoesNotExist:
            if self.allow_non_fk and data:
                return None, data[1]
            else:
                return None, None

        return obj.pk, unicode(obj)


class AjaxSuggestField(forms.Field):
    def __init__(self, model, allow_non_fk=False, extra_suggest_options=None, *args, **kwargs):
        super(AjaxSuggestField, self).__init__(*args, **kwargs)
        self.model = model
        self.allow_non_fk = allow_non_fk
        self.widget = AjaxSuggestWidget(model, allow_non_fk=allow_non_fk, extra_suggest_options=extra_suggest_options)

    def clean(self, value):

        if not self.required and not value[0]:
            return None if not self.allow_non_fk else value[1]

        try:
            obj = self.model.objects.get(pk=value[0])
        except self.model.DoesNotExist:
            if self.allow_non_fk and value[1]:
                return value[1]
            else:
                raise forms.ValidationError(u'Нет такого родительского объекта')
        except TypeError:
            if self.required:
                #  Нет значения, обращение по индексу вызывает исключение
                raise forms.ValidationError(u'Не указано значение')
            else:
                return None
        return obj
