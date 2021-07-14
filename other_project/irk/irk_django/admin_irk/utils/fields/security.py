# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from captcha.fields import CaptchaField as BaseCaptchaField, CaptchaTextInput as BaseCaptchaTextInput


class CaptchaTextInput(BaseCaptchaTextInput):
    def __init__(self, *args, **kwargs):
        if not 'output_format' in kwargs:
            kwargs['output_format'] = settings.CAPTCHA['OUTPUT_FORMAT']
        super(CaptchaTextInput, self).__init__(*args, **kwargs)


class CaptchaField(BaseCaptchaField):
    """Перегруженное поле капчи, которому можно задавать виджет"""

    def __init__(self, widget=None, *args, **kwargs):
        fields = (
            forms.CharField(show_hidden_initial=True),
            forms.CharField(),
        )
        if 'error_messages' not in kwargs or 'invalid' not in kwargs.get('error_messages'):
            if 'error_messages' not in kwargs:
                kwargs['error_messages'] = dict()
            kwargs['error_messages'].update(dict(invalid=_('Invalid CAPTCHA')))

        if not widget:
            widget_kwargs = dict(
                output_format=kwargs.get('output_format') or settings.CAPTCHA['OUTPUT_FORMAT']
            )
            for k in ('output_format',):
                if k in kwargs:
                    del (kwargs[k])
            widget = CaptchaTextInput(**widget_kwargs)

        super(BaseCaptchaField, self).__init__(fields=fields, widget=widget, *args, **kwargs)
