# -*- coding: utf-8 -*-

import functools


def render_to_string_with_context(func):
    """Декоратор `django.template.loader.render_to_string`, для получения контекста шаблона"""

    @functools.wraps(func)
    def wrapper(template_name, context=None, *args, **kwargs):
        result = func(template_name, context, *args, **kwargs)
        result.context = context or {}

        return result

    return wrapper
