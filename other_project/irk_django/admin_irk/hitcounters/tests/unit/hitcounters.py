# -*- coding: utf-8 -*-

import redis

from irk.map.models import Cities as City
from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase

from irk.hitcounters import settings
from irk.hitcounters.actions import _object_key


class HitCountersTest(UnitTestBase):

    def test_updating(self):
        news_site = Site.objects.get(slugs='news')
        city = City.objects.get(alias='irkutsk')

        news = create_material(
            'news', 'news', city=city, sites=[news_site, ], slug=self.random_string(5).lower(), site=news_site,
            is_hidden=False, content='Irkutsk Times', last_comment=None, bunch=None, n=1
        )

        connection = redis.StrictRedis(host=settings.REDIS_DB['HOST'], db=settings.REDIS_DB['DB'])
        connection.flushdb()
        obj_key = _object_key(news)
        value = int(connection.get(obj_key) or 0)
        self.assertEqual(0, value)

        self.app.get(news.get_absolute_url())
        value = int(connection.get(obj_key) or 0)
        self.assertEqual(1, value)

        self.app.get(news.get_absolute_url())
        value = int(connection.get(obj_key) or 0)
        self.assertEqual(1, value)
