# -*- coding: utf-8 -*-

import datetime

from django.core.urlresolvers import reverse

from irk.home import settings as app_settings
from irk.map.models import Cities as City
from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase


class NewsTest(UnitTestBase):
    """Тесты новостей на главной странице"""

    def setUp(self):
        self.home_site = Site.objects.get(slugs='home')
        self.news_site = Site.objects.get(slugs='news')
        self.city_irkutsk = City.objects.get(alias='irkutsk')
        self.admin = self.create_user('admin', 'admin', is_admin=True)
        self.url = reverse('home_index')

    def _create_news(self, n, **kwargs):
        now = datetime.datetime.now()
        attrs = {
            'sites': [self.news_site, ],  # новости из раздела news
            'is_hidden': False,
            'stamp': now.date(),
            'published_time': now.time(),
            'site': self.news_site,
            'last_comment': None,
            'fill_nullable_fields': False,
        }
        attrs.update(**kwargs)

        return create_material('news', 'news', n=n, **attrs)

    def _get_materials(self, user=None):
        return self.app.get(self.url, user=user).context['materials']

    def test_main_and_latest_news(self):
        """На главной странице выводятся новости"""

        # создадим 10 новостей
        news = self._create_news(n=app_settings.HOME_NEWS_COUNT)
        response = self.app.get(self.url)

        # они выводятся
        self.assertIn('news', response.context)
        self.assertEqual(response.context['news']['main'], news[0])
        self.assertEqual(len(response.context['news']['last']), app_settings.HOME_NEWS_COUNT-1)

        # данные для кнопки Показать еще
        self.assertIn('next_start_index', response.context['news'])
        self.assertEqual(response.context['news']['next_start_index'], app_settings.HOME_NEWS_COUNT)

    def test_show_more(self):
        """Вью для кнопка Показать еще возвращает данные"""

        self._create_news(n=5, title='my title')
        response = self.app.get(self.url, xhr=True)

        self.assertStatusIsOk(response)
        self.assertContains(response, 'my title', count=5)

    def test_pagination(self):
        """Пейджинация работает"""

        self._create_news(n=5, title='my title')
        response = self.app.get(self.url, {'start': '1', 'limit': '2'}, xhr=True)

        self.assertStatusIsOk(response)
        self.assertContains(response, 'my title', count=2)
        self.assertTrue(response.json['has_next'])
        self.assertEqual(response.json['next_limit'], 2)
        self.assertEqual(response.json['next_start_index'], 3)
