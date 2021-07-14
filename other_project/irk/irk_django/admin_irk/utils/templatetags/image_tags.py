# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def image_line_height(context, width, image_width, image_height, _, var):
    if all([width, image_width, image_height]):
        context[var] = width - image_width + image_height
    return ""
