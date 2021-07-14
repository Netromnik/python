# -*- coding: utf-8 -*-

from __future__ import absolute_import

import redis

from time import sleep

from django.conf import settings

from irk.utils.cache_ids import cached_ids

from irk.tests.unit_base import UnitTestBase


class CacheIdsTest(UnitTestBase):

    def test_cache(self):

        IDS_LIST = [1, ]

        @cached_ids(expire=3)
        def return_id_test_function_8khbr479okdos9ekrjsd():
            # При каждом вызове функции выводить новое значение
            value = IDS_LIST[-1] + 1
            IDS_LIST.append(value)
            return IDS_LIST

        r = redis.StrictRedis(host=settings.REDIS['default']['HOST'], db=settings.REDIS['default']['DB'])

        ids = list(r.smembers('return_id_test_function_8khbr479okdos9ekrjsd'))
        self.assertFalse(ids)

        # Ожидаем значение из функции
        self.assertEquals(sorted(return_id_test_function_8khbr479okdos9ekrjsd().get_ids()), sorted([1, 2]))

        # Проверяем содеожание кэша
        ids = list(r.smembers('return_id_test_function_8khbr479okdos9ekrjsd'))
        ids = [int(i) for i in ids]
        self.assertEquals(sorted(ids), sorted([1, 2]))

        # Ожидаем значение из кэша
        self.assertEquals(sorted(return_id_test_function_8khbr479okdos9ekrjsd().get_ids()), sorted([1, 2]))

        # Ждем протухания кэша
        sleep(4)

        # Ожидаем значение из функции
        self.assertEquals(sorted(return_id_test_function_8khbr479okdos9ekrjsd().get_ids()), sorted([1, 2, 3]))

        # Проверяем содеожание кэша
        ids = list(r.smembers('return_id_test_function_8khbr479okdos9ekrjsd'))
        ids = [int(i) for i in ids]
        self.assertEquals(sorted(ids), sorted([1, 2, 3]))

        # Ожидаем значение из кэша
        self.assertEquals(sorted(return_id_test_function_8khbr479okdos9ekrjsd().get_ids()), sorted([1, 2, 3]))

        # Проверка функции очистки кэша
        return_id_test_function_8khbr479okdos9ekrjsd().clear_cache()
        ids = list(r.smembers('return_id_test_function_8khbr479okdos9ekrjsd'))
        self.assertFalse(ids)

        # Ожидаем значение из функции
        self.assertEquals(sorted(return_id_test_function_8khbr479okdos9ekrjsd().get_ids()), sorted([1, 2, 3, 4]))
