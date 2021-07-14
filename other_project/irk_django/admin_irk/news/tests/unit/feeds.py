# -*- coding: utf-8 -*-

import datetime
import feedparser

from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase
from irk.options.models import Site

from irk.news.tests.unit.material import create_material


class YandexFeedTestCase(UnitTestBase):
    """Тестирование RSS ленты для Яндекса"""

    # TODO: тест на проверку того, что новости, созданные только что, не должны выводиться в ленте
    # TODO: тест вывода главного изображения новости

    def _get_news(self, amount, **kwargs):
        site = Site.objects.get(slugs='news')

        created = datetime.datetime.now() - datetime.timedelta(days=1)
        return create_material('news', 'news', created=created, sites=[site], n=amount, **kwargs)

    def test_length(self):
        """В ленте выводится 15 записей"""

        self._get_news(20, is_hidden=False, is_payed=False)

        feed = feedparser.parse(self.app.get(reverse('news:yandex_rss')).body)
        self.assertEqual(len(feed['entries']), 15)

    def test_hidden(self):
        """В ленте не должны выводиться скрытые новости"""

        self._get_news(3, is_hidden=True)

        feed = feedparser.parse(self.app.get(reverse('news:yandex_rss')).body)
        self.assertEqual(len(feed['entries']), 0)

    def test_payed(self):
        """В ленте не должны выводиться платные новости"""

        self._get_news(3, is_payed=True)

        feed = feedparser.parse(self.app.get(reverse('news:yandex_rss')).body)
        self.assertEqual(len(feed['entries']), 0)

    def test_exported(self):
        """В ленте не должны выводиться новости с отметкой is_exported=False"""

        news = self._get_news(3, is_exported=False, is_hidden=False, is_payed=False)

        feed = feedparser.parse(self.app.get(reverse('news:yandex_rss')).body)
        self.assertEqual(len(feed['entries']), 0)

        for entry in news:
            entry.is_exported = True
            entry.save()

        feed = feedparser.parse(self.app.get(reverse('news:yandex_rss')).body)
        self.assertEqual(len(feed['entries']), 3)
