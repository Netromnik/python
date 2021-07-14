# -*- coding: UTF-8 -*-
from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase

from irk.news.models import Live, LiveEntry
from irk.news.tests.unit.material import create_material


class LiveNewsTestCase(UnitTestBase):
    """Тесты текстовых трансляций"""

    def test_ajax_update(self):
        """Получить html с записями конкретной трансляции"""

        live = G(Live)
        G(LiveEntry, live=live, n=5)
        response = self.app.get(reverse('news:live:update', args=(live.id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/snippets/live_table_content.html')
        self.assertEqual(len(response.context['entries']), 5)

    def test_yandex_live_feed(self):
        """Для rss яндекса"""

        news = create_material('news', 'news')
        live = G(Live, news=news)
        G(LiveEntry, live=live, n=5)
        response = self.app.get(reverse('news:live:feed', args=(live.id, )))
        self.assertEqual(response.status_code, 200)
