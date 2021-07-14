# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time

from django.core.cache import cache
from irk.utils.cache import TagCache
from irk.utils import settings as app_settings
from irk.tests.unit_base import UnitTestBase


class TagCacheTest(UnitTestBase):

    def test(self):
        key = 'foo'
        expire = 60 * 60
        tags = ('news', 'gallery')
        result = u'result'

        tag_cache = TagCache(key, expire, tags)

        value = tag_cache.value
        self.assertEqual(value, tag_cache.EMPTY)

        tag_cache.value = result
        for tag in tags:
            value = app_settings.CACHE_TAG_PREFIX % tag
            self.assertIsNotNone(cache.get(value))

        self.assertIsNotNone(cache.get(key))

        # Инвалидируем один из тегов
        cache.delete(app_settings.CACHE_TAG_PREFIX % tags[0])
        # Кэшируемый объект теперь невалиден
        self.assertEqual(TagCache.EMPTY, tag_cache.value)
