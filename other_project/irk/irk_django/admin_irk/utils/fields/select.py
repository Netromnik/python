# -*- coding: utf-8 -*-

import re

from django.core.exceptions import ObjectDoesNotExist
from django.forms import MultipleChoiceField, models, ModelMultipleChoiceField, TextInput, CharField, MultiWidget
from django.template.loader import render_to_string

EMPTY_VALUES = (None, '', 'None')


class IntField(models.Field):
    multiple = False

    def db_type(self):
        return 'text'

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        cls._meta.add_field(self)
        main = self

        def getDispl(self):
            string = ''
            for obj in main.value_from_object(self):
                for i in main.choices:
                    if i[0] == obj:
                        string += '%s ' % i[1]
            return string

        def get(self):
            return main.value_from_object(self)

        setattr(cls, 'get_%s_display' % self.name, getDispl)
        setattr(cls, 'get_%s' % self.name, get)

    def formfield(self, *args, **kwargs):
        if not self.multiple:
            return models.Field.formfield(self, **kwargs)
        else:
            defaults = {'label': self.verbose_name, 'choices': self.choices}
            defaults.update(kwargs)
            return MultipleChoiceField(**defaults)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        return ";".join(value)

    def value_from_object(self, obj):
        value = getattr(obj, self.attname)
        if value:
            values = value.strip().split(";")
            result = []
            for val in values:
                try:
                    val = int(val)
                except:
                    pass
                result.append(val)
            return result
        else:
            return []

    def __init__(self, *args, **kwargs):
        if "multiple" in kwargs:
            self.multiple = kwargs['multiple']
            del kwargs['multiple']
        models.Field.__init__(self, *args, **kwargs)


class AjaxInputWidget(TextInput):
    url = ""
    callback = None

    def render(self, name, value, attrs=None, renderer=None):
        url = self.url
        callback = self.callback
        context = {
            "url": url,
            "callback": callback,
            "name": name,
            "value": value,
            "attrs": attrs,
        }
        return render_to_string("widget/AjaxTextInput.html", context)


class AjaxTextField(CharField):
    url = ""
    callback = None
    widget = AjaxInputWidget

    def __init__(self, url, callback, *args, **kwargs):
        self.url = url
        self.callback = callback
        super(AjaxTextField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        widget.callback = self.callback
        widget.url = self.url


class AjaxSuggestWidget(TextInput):
    template_name = 'widget/MultiAjaxSuggestWidget.html'

    def __init__(self, queryset, url, callback, required, new=False, *args, **kwargs):
        self._queryset = queryset
        self._url = url
        self._callback = callback
        self._new = new
        self._required = required

        super(AjaxSuggestWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super(AjaxSuggestWidget, self).get_context(name, value, attrs)
        context['widget']['type'] = self.input_type

        value_text = None
        if value:
            try:
                value_text = self._queryset.get(pk=value)
            except ObjectDoesNotExist:
                pass

        context['widget'].update({
            'value_text': value_text,
            'url': self._url,
            'callback': self._callback,
            'idx': int(re.findall(r'\d+', name)[0]),
            'new': self._new,
        })

        return context


class MultiAjaxSuggestWidget(MultiWidget):
    def __init__(self, queryset, url, callback, amount, required, new=False, *args, **kwargs):
        """
        params - дополнительные параметры к GET запросу для автокомплита
        """
        widgets = [AjaxSuggestWidget(queryset, url, callback, required, new=new, *args, **kwargs), ] * amount
        super(MultiAjaxSuggestWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        # Непонятно зачем вызывается этот метод, когда у нас есть self.widgets
        return ()


class MultiAjaxTextField(ModelMultipleChoiceField):
    """Несколько autocomplete полей для M2M связей"""

    def __init__(self, queryset, required=True, url='', callback='', amount=0, new=False, *args, **kwargs):
        super(MultiAjaxTextField, self).__init__(queryset,
                                                 **kwargs)
        self.widget = MultiAjaxSuggestWidget(queryset, url, callback, amount, required, new=new)

    def clean(self, value):
        value = filter(lambda x: x, value)
        return super(MultiAjaxTextField, self).clean(value)
