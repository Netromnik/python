# -*- coding: utf-8 -*-

import os

from django import template
from django.db.models import Model

register = template.Library()


@register.filter
def classname(obj):
    type_ = type(obj)
    return type_.__name__


@register.filter
def ctime(path):
    """
    Возвращает время последнего изменения метаданных файла/папки по пути path.
    Используется для добавления верифицирующих параметров.

    :param str path: путь до файла/папки
    """

    try:
        return int(os.stat(path).st_ctime)
    except (TypeError, OSError, AttributeError):
        return ''


@register.filter
def verbose_name(instance):
    """
    Подробное название для экземпляра модели

    См. также: BaseMaterial.label
    :param Model instance: экземпляр модели
    :return str: подробное название
    """

    if not isinstance(instance, Model):
        return ''

    opts = instance._meta

    return opts.verbose_name


@register.filter
def verbose_name_plural(instance):
    """
    Подробное название для множественного числа

    :param Model instance: экземпляр модели
    :return str: подробное название
    """

    if not isinstance(instance, Model):
        return ''

    opts = instance._meta

    return opts.verbose_name_plural
