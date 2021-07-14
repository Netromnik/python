# -*- coding: utf-8 -*-

"""Виджет для выбора уровня звезд"""

from django import forms
from django.template.loader import render_to_string


class StarSelectWidget(forms.Widget):
    def __init__(self, amount=5, default=3, *args, **kwargs):
        if default > amount:
            raise Exception(u'Количество звезд по умолчанию больше, чем суммарное')
        self._amount = amount
        self._default = default
        super(StarSelectWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        data = {
            'name': name,
            'value': value,
            'attrs': attrs,
            'amount': self._amount,
            'default': self._default,
            'rng': range(1, self._amount + 1)
        }

        return render_to_string('widget/StarSelect.html', data)
