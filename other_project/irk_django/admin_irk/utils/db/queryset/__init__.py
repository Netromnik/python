# -*- coding: utf-8 -*-

import hashlib

import redis
from django.db.models.query import QuerySet
from django.db.models.sql.where import WhereNode


#TODO используется
def cached_queryset(queryset, clear_related_lookups=False):
    """Враппер для QuerySet, кэширующий порядок следования элементов в кэш

    При первом выполнении в кэше сохраняются id объектов,
    при последующих выборках из QuerySet убирается весь order_by и параметры фильтрации,
    объекты выбираются по PK и затем сортируются"""

    raw_queryset = queryset
    r = redis.StrictRedis()

    key = 'query.ordering.%(app)s.%(model)s.%(hash)s' %  {
        'app': raw_queryset.model._meta.app_label,
        'model': raw_queryset.model._meta.object_name.lower(),
        'hash': hashlib.sha1(str(raw_queryset.query)).hexdigest(),
    }

    ids = r.lrange(key, queryset.query.low_mark or 0, queryset.query.high_mark or -1)
    if not ids:
        ids = list(raw_queryset.values_list('id', flat=True))
        if ids:
            r.rpush(key, *ids)
        r.expire(key, 1000*60*60*24)

        return raw_queryset

    else:
        ids = [int(x) for x in ids]

        # Обнуляем у запроса блоки WHERE и ORDER BY
        query = raw_queryset.query.clone()
        query.where = WhereNode()
        query.distinct = False
        query.clear_ordering(force_empty=True)
        query.clear_deferred_loading()
        query.clear_select_fields()
        query.clear_limits()

        queryset = QuerySet(raw_queryset.model, query=query).filter(id__in=sorted(ids))
        queryset = list(queryset)

        return sorted(queryset, key=lambda x: ids.index(x.id))


def invalidate_queryset_cache(model_cls):
    """Удаление всех ключей модели, хранящих порядок сортировки"""
    return  # TODO: временно не используется
    '''
    base_key = 'query.ordering.%s.%s.*' % (model_cls._meta.object_name.lower(), model_cls._meta.object_name.lower())
    r = redis.StrictRedis()

    pipe = r.pipeline()
    pipe.delete(r.keys(base_key))
    pipe.execute()
    '''
