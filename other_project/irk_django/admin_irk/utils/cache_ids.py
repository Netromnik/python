# -*- coding: utf-8 -*-

import redis

from django.conf import settings


class CacheIds(object):
    def __init__(self, func, expire):
        self.key = func.__name__
        self.func = func
        self.expire = expire
        self.r = redis.StrictRedis(host=settings.REDIS['default']['HOST'], db=settings.REDIS['default']['DB'])

    def get_ids(self):
        ids = list(self.r.smembers(self.key))

        if not ids:
            ids = self.func()
            # не работает в старом redis < 2.4
            #self.r.sadd(self.key, *ids)
            for idx in ids:
                self.r.sadd(self.key, idx)
            self.r.expire(self.key, self.expire)
        else:
            ids = [int(i) for i in ids]

        return ids

    def clear_cache(self):
        self.r.delete(self.key)


def cached_ids(expire=60):
    """ Декоратр для кэширования id в редисе. Ключ - название декорируемой функции.
        Возвращает объект содержащий значение из кэша по ключу.
        Если не находит возвращает объект со значением из функции."""

    def decorator(func):

        def wrapper():

            return CacheIds(func, expire)

        return wrapper

    return decorator
