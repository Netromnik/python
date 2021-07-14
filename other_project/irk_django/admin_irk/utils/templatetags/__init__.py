# -*- coding: utf-8 -*-

from django import template
from django.template.base import kwarg_re


def parse_arguments(parser, bits):
    """Парсинг параметров, переданных шаблонному тегу

    Скопирован из исходников django, поддерживает как позиционные, как именованные аргументы"""

    args = []
    kwargs = {}

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise template.TemplateSyntaxError("Malformed arguments to tag")
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))

    return args, kwargs
