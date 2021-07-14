# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import warnings
import functools
import datetime
import time

from django import forms
from django.conf import settings
from django.utils.http import http_date


logger = logging.getLogger(__name__)


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function %(funcname)s." % {
                'funcname': func.__name__,
            },
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1
        )
        logger.warning('Deprecated function `%(funcname)s` called at %(filename)s:%(lineno)d' % {
            'funcname': func.__name__,
            'filename': func.func_code.co_filename,
            'lineno': func.func_code.co_firstlineno + 1,
        })
        return func(*args, **kwargs)

    return new_func


def nginx_cached(seconds, test_func=None):
    """Добавление кэширующих заголовков"""

    def cached_functions(func):
        def wrapper(request, *args, **kwargs):
            now = datetime.datetime.now()
            result = func(request, *args, **kwargs)
            if not settings.DEBUG and (not test_func or test_func(request, *args, **kwargs)):
                exp = now + datetime.timedelta(seconds=seconds)
                result['Cache-Control'] = 'public, max-age=%s, must-revalidate' % seconds
                result['Expires'] = http_date(time.mktime(exp.timetuple()))
                result['Last-Modified'] = http_date()
                # Удаляем cookies из ответа
                del result['Set-Cookie']

                # Ставим метку, чтобы CSRF не ставил свою куку
                request.META['CSRF_COOKIE'] = None

            return result

        return wrapper

    return cached_functions


def strip_fields(cls):
    """Декоратор форм, автоматически делающий .strip() значения CharField при валидации

    Source: https://bitbucket.org/offline/django-annoying/src/tip/annoying/decorators.py
    """

    # TODO: Не работает в формах админки

    fields = [(key, value) for key, value in cls.base_fields.iteritems() if isinstance(value, forms.CharField)]
    for field_name, field_object in fields:
        def get_clean_func(original_clean):
            return lambda value: original_clean(value and value.strip())

        clean_func = get_clean_func(getattr(field_object, 'clean'))
        setattr(field_object, 'clean', clean_func)
    return cls


def options(**kwargs):
    """
    Декоратор для установки свойств у функции или метода

    >>> @options(allow_tags=True)
    ... def give_me_the_money():
    ...     pass
    ...
    >>> assert getattr(give_me_the_money, 'allow_tags') == True
    """

    def decorator(func):
        for key, value in kwargs.items():
            setattr(func, key, value)

        return func

    return decorator


def memoized(func):
    """
    Кеширует ответ оборачиваемой функции
    Аналог lru_cache из python3
    """
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return wrapper
