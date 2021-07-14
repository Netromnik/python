# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.map.models import Cities as City
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase

from irk.news.models import ArticleType
from irk.news.tests.unit.material import create_material


class NewsTestCase(UnitTestBase):
    """Тесты новостей"""

    def setUp(self):
        super(NewsTestCase, self).setUp()
        self.admin = self.create_user('admin', '123', is_admin=True)
        self.site = Site.objects.get(slugs='news')
        self.city = City.objects.get(alias='irkutsk')
        self.stamp = datetime.date.today()

    def test_read(self):
        """Страница новости"""

        slug = self.random_string(10).lower()
        news = create_material('news', 'news', slug=slug, stamp=self.stamp, city=self.city, is_hidden=False)
        kwargs_ = {
            "year": self.stamp.year,
            "month": '%02d' % self.stamp.month,
            "day": '%02d' % self.stamp.day,
            "slug": slug,
        }
        response = self.app.get(reverse('news:news:read', kwargs=kwargs_))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/news/read.html')
        self.assertEqual(news, response.context['object'])
        self.validate_meta_tags(response)

        news.is_hidden = True
        news.save()

        response = self.app.get(reverse('news:news:read', kwargs=kwargs_), status='*')
        self.assertEqual(response.status_code, 404)

        response = self.app.get(reverse('news:news:read', kwargs=kwargs_), user=self.admin)
        self.assertEqual(response.status_code, 200)

    def test_related_news(self):
        """Предыдущая и следующая новости"""

        prev_news = create_material('news', 'news', slug=self.random_string(10).lower(), is_hidden=False)
        news = create_material('news', 'news', bunch=prev_news, slug=self.random_string(10).lower(), is_hidden=False)
        next_news = create_material('news', 'news', bunch=news, slug=self.random_string(10).lower(), is_hidden=False)

        response = self.app.get(news.get_absolute_url(), status='*')

        self.assertEqual(prev_news, response.context['previous_news'])
        self.assertEqual(next_news, response.context['continuation_news'])

    def test_related_news_when_they_are_hidden(self):
        """Предыдущая и следующая новости скрыты"""

        prev_news = create_material('news', 'news', is_hidden=True, slug=self.random_string(10).lower())
        news = create_material('news', 'news', is_hidden=False, bunch=prev_news, slug=self.random_string(10).lower())
        next_news = create_material('news', 'news', is_hidden=True, bunch=news, slug=self.random_string(10).lower())

        response = self.app.get(news.get_absolute_url(), status='*')

        self.assertIsNone(response.context['previous_news'])
        self.assertIsNone(response.context['continuation_news'])

        response = self.app.get(news.get_absolute_url(), user=self.admin, status='*')

        self.assertEqual(prev_news, response.context['previous_news'])
        self.assertEqual(next_news, response.context['continuation_news'])


class SearchTestCase(UnitTestBase):
    """Поиск в новостях"""

    def test_search(self):
        """Страница поиска"""

        response = self.app.get(reverse('news:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/search.html')

    def test_search_ajax(self):
        """Страница поиска получаемая аяксом"""

        response = self.app.get(reverse('news:search'), headers={'X_REQUESTED_WITH': 'XMLHttpRequest', })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/search/snippets/entries.html')


class SameAlias(UnitTestBase):
    """Проверка когда за один день есть новость и статья с одним алиасом"""

    def test(self):
        news_site = Site.objects.filter(slugs="news")[0]
        stamp = datetime.date.today()
        alias = self.random_string(5).lower()
        news_title = "This is news title"
        article_title = "This is article title"
        news_content = "This is news content"
        article_content = "This is article content"
        news = create_material(
            'news', 'news', slug=alias, stamp=stamp, title=news_title, is_hidden=False, content=news_content
        )
        result = self.app.get(news.get_absolute_url())

        self.assertEqual(200, result.status_code)
        self.assertEqual(result.context['object'].title, news_title)
        self.assertEqual(result.context['object'].content, news_content)

        article_type = G(ArticleType)
        article = create_material(
            'news', 'article', slug=alias, title=article_title, type=article_type, content=article_content,
            article_ptr__last_comment=None, last_comment=None, is_hidden=False, stamp=stamp
        )
        result = self.app.get(article.get_absolute_url())

        self.assertEqual(200, result.status_code)
        self.assertEqual(result.context['object'].title, article_title)
        self.assertEqual(result.context['object'].content, article_content)


class CalendarTestCase(UnitTestBase):
    """Блок календаря"""

    def test_calendar(self):
        """Запрос на показ блока календаря в новостях"""

        params = {'highlight': datetime.date.today().strftime('%Y%m%d')}
        response = self.app.get(reverse('news:calendar'), params=params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/tags/calendar.html')
