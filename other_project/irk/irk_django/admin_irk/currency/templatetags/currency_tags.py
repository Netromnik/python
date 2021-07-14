# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter
def unsigned2_2f(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0
    return ('%2.2f' % value).replace('.', ',')


@register.filter
def signed2_2f(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0
    if value > 0:
        return ('+%2.2f' % value).replace('.', ',')
    elif value < 0:
        return ('%2.2f' % value).replace('.', ',')
    return '0,00'
