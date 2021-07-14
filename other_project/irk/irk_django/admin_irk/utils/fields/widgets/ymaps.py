# -*- coding: utf-8 -*-

from django.forms import widgets
from django.template.loader import render_to_string


class YMapsPointWidget(widgets.Input):
    input_type = 'hidden'

    class Media:
        js = (
            'https://api-maps.yandex.ru/2.0-stable/?load=package.standard&lang=ru-RU',
        )

    def render(self, name, value, attrs=None, renderer=None):
        html = super(YMapsPointWidget, self).render(name, value, attrs)

        return html + render_to_string('forms/fields/widgets/ymaps/point.html', {
            'name': name,
            'value': value,
            'attrs': attrs,
        })
