# -*- coding: utf-8 -*-

from django import template
from django.http import Http404
from django.template.loader import render_to_string

from irk.news.models import Photo, Article, Infographic
from irk.utils.templatetags import parse_arguments

register = template.Library()


@register.tag
def special_material_card(parser, token):
    """
    Карточка материала для спецпроекта

    Параметры:
        material - материал, наследник news.BaseMaterial
        metrika_goal - цель для Яндекс.Метрики

        другие именнованные параметры просто передаются в шаблон
    """

    bits = token.split_contents()
    args, kwargs = parse_arguments(parser, bits[1:])

    return SpecialMaterialCardNode(*args, **kwargs)


class SpecialMaterialCardNode(template.Node):
    """Нода для карточки материала в спецпроекте"""

    def __init__(self, material, **kwargs):
        self._material = material
        self._kwargs = kwargs

    def render(self, context):
        material = self._material.resolve(context)
        if not material:
            return ''

        kwargs = {key: value.resolve(context) for key, value in self._kwargs.items()}

        template_context = {
            'material': material,
            'request': context.get('request'),
        }
        template_context.update(kwargs)

        return render_to_string(self.get_template(material), template_context)

    def get_template(self, material):
        """Получить шаблон для отображения материала"""

        return [
            'special/tags/material_card/{}.html'.format(material._meta.model_name),
            'special/tags/material_card/article.html',
        ]
