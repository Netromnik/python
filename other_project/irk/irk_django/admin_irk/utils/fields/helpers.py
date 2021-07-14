# -*- coding: utf-8 -*-


def field_verbose_name(obj, field_name):
    """
    Возвращает полное название поля модели

    :type obj: django.db.models.Model
    :type field_name: str
    """
    
    opts = obj._meta

    return opts.get_field(field_name).verbose_name
