# -*- coding: utf-8 -*-

import warnings

import redis
from django.conf import settings


def get_redis(database_name='default', **kwargs):
    """Возвращается клиент к redis базе

    Параметры::
        database_name : имя базы из `django.conf.settings.REDIS`
    """

    opts = settings.REDIS
    if database_name not in opts:
        warnings.warn('Redis database {0} is unavailable. Falling back to default'.format(database_name), RuntimeWarning)
        database_name = 'default'

    return redis.StrictRedis(host=opts[database_name]['HOST'], db=opts[database_name]['DB'], **kwargs)
