# -*- coding: utf-8 -*-

# TODO: docstring

from django import template

register = template.Library()


@register.inclusion_tag('snippets/2date.html')
def date_date(date1, date2, dir=False, short=True):
    # TODO: docstring
    if dir == 'False':
        dir = False
    if short == 'False':
        short = False
    return {'date1': date1, 'date2': date2, 'dir': dir, 'short': short}
