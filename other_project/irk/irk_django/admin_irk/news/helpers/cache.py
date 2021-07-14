# -*- coding: utf-8 -*-

"""Кэширование списка материалов для раздела Новости"""

import logging

from django.contrib.contenttypes.models import ContentType

from irk.utils.db.kv import get_redis
from irk.utils.helpers import int_or_none

logger = logging.getLogger(__name__)

BASE_MATERIAL_KEY = 'news.index.materials'


def save_to_cache(key, materials):
    """
    Сохранить материалы в кэш

    :param str key: постфикс ключа для кэша
    :param QuerySet|list materials: список материалов
    """

    full_key = '{}.{}'.format(BASE_MATERIAL_KEY, key)
    if hasattr(materials, 'values'):
        # это queryset
        materials = list(materials.values('content_type_id', 'pk'))

    redis = get_redis()
    pipe = redis.pipeline()
    pipe.delete(full_key)
    for material in materials:
        if isinstance(material, dict):
            value = '{}.{}'.format(material['content_type_id'], material['pk'])
        else:
            value = '{}.{}'.format(material.content_type_id, material.pk)
        pipe.rpush(full_key, value)

    result = any(pipe.execute())

    if result:
        logger.debug('Save materials for key: %s', full_key)
    else:
        logger.warn('Can not save materials: %s, %s', full_key, result)

    del redis


def load_from_cache(key):
    """
    Загрузить материалы из кэша

    :param str key: постфикс ключа для кэша
    """

    full_key = '{}.{}'.format(BASE_MATERIAL_KEY, key)

    redis = get_redis()
    data = redis.lrange(full_key, 0, -1)
    del redis

    materials_by_ct = {}
    for row in data:
        ct_pk, material_pk = row.split('.')
        ct_pk = int_or_none(ct_pk)
        material_pk = int_or_none(material_pk)
        if not ct_pk or not material_pk:
            logger.warning('Not ct_pk or material_pk. It is impossible to restore the object')
            continue
        ct = ContentType.objects.get_for_id(ct_pk)
        materials_by_ct.setdefault(ct, []).append(material_pk)

    materials = []
    for ct, material_ids in materials_by_ct.items():
        model = ct.model_class()
        materials.extend(model.objects.filter(pk__in=material_ids))

    def key_function(obj):
        """Ключ сортировки для материалов"""
        ct_pk = ContentType.objects.get_for_model(obj, for_concrete_model=False).pk

        return data.index('{}.{}'.format(ct_pk, obj.pk))

    return sorted(materials, key=key_function)


def clear_cache():
    """Удалить все материалы сохраненные в кэше"""

    redis = get_redis()

    keys = redis.keys('{}.*'.format(BASE_MATERIAL_KEY))
    if keys:
        redis.delete(*keys)

    del redis
