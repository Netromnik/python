# -*- coding: UTF-8 -*-

from __future__ import absolute_import

import datetime
import json

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase

from irk.obed.models import ArticleCategory


class ObedArticlesTestCase(UnitTestBase):
    """Тестирование статей обеда"""

    def setUp(self):
        super(ObedArticlesTestCase, self).setUp()
        self.categories = [
            G(ArticleCategory, title=u'Критик', slug='critic'),
            G(ArticleCategory, title=u'Новости', slug='news'),
            G(ArticleCategory, title=u'Рецепты', slug='recipes'),
        ]
        self.admin = self.create_user('admin', 'admin', is_admin=True)
        self.site = Site.objects.get(slugs='obed')

    def test_article_page(self):
        """Статьи обеда"""

        title = self.random_string(10)
        slug = self.random_string(5).lower()
        today = datetime.date.today()
        article = create_material(
            'obed', 'article', slug=slug, stamp=today, title=title, section_category=self.categories[0],
            site=self.site, sites=[self.site], is_hidden=False
        )

        url_args = (today.year, '%02d' % today.month, '%02d' % today.day, slug)
        result = self.app.get(reverse('obed:article:read', args=url_args))
        self.assertEqual(200, result.status_code)
        self.assertTemplateUsed(result, 'obed/article/read.html')
        self.assertEqual(result.context['object'].title, title)

        article.is_hidden = True
        article.save()

        result = self.app.get(reverse('obed:article:read', args=url_args), status='*')
        self.assertEqual(404, result.status_code)

        result = self.app.get(reverse('obed:article:read', args=url_args), user=self.admin)
        self.assertEqual(200, result.status_code)

    def test_article_see_also(self):
        """Аякс эндпоинт блока "Смотри также" """

        today = datetime.date.today()
        create_material(
            'obed', 'article', n=10, stamp=today, section_category=self.categories[1], site=self.site,
            sites=[self.site], is_hidden=False
        )
        create_material(
            'obed', 'article', n=20, stamp=today, section_category=self.categories[0], site=self.site,
            sites=[self.site], is_hidden=False
        )

        url = reverse('obed:article:see_also_list', kwargs={'category_id': self.categories[0].pk})

        response = self.app.get(url, params={'start': 7, 'limit': 6}, xhr=True)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertTrue(data['has_next'])
        self.assertEqual(data['next_limit'], 6)
        self.assertEqual(data['next_start_index'], 13)

        response = self.app.get(url, params={'start': 13, 'limit': 6}, xhr=True)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertTrue(data['has_next'])
        self.assertEqual(data['next_limit'], 1)
        self.assertEqual(data['next_start_index'], 19)

        response = self.app.get(url, params={'start': 19, 'limit': 6}, xhr=True)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertFalse(data['has_next'])
        self.assertEqual(data['next_limit'], 0)
        self.assertEqual(data['next_start_index'], 20)

    def test_articles_index(self):
        """Индекс статей обеда"""
        self._populate_articles()

        result = self.app.get(reverse('obed:article:index'))
        self.assertEqual(200, result.status_code)
        self.assertTemplateUsed(result, 'obed/article/index.html')
        self.assertEqual(len(result.context['object_list']) > 0, True)

    def test_ajax_articles(self):
        """Получение списка статей Ajax-запросом"""
        self._populate_articles()

        url = reverse('obed:article:index')
        result = self.app.get(url, xhr=True)

        self.assertEqual(200, result.status_code)
        self.assertTemplateUsed(result, 'obed/article/article_list.html')
        self.assertEqual(9, len(result.context['object_list']))
        # NOTE: На данный момент пагинация используется постоянно. По умолчанию отдается 20 статей.
        self.assertIsNotNone(result.context['page_obj'])

    def test_ajax_articles_with_limit(self):
        """Получение списка статей Ajax-запросом постранично"""
        self._populate_articles()

        url = reverse('obed:article:index')
        result = self.app.get(url, params={'limit': 3}, xhr=True)

        self.assertEqual(200, result.status_code)
        self.assertTemplateUsed(result, 'obed/article/article_list.html')
        self.assertEqual(3, len(result.context['object_list']))
        self.assertIsNotNone(result.context['page_obj'])

    def test_articles_subcategory(self):
        """Индекс подрубрики статей обеда"""
        self._populate_articles_for_category(self.categories[0])

        result = self.app.get(reverse('obed:article:category',
                                      kwargs={'section_category_slug': self.categories[0].slug}))
        self.assertEqual(200, result.status_code)
        self.assertTemplateUsed(result, 'obed/article/index.html')
        self.assertEqual(len(result.context['objects'].object_list), 3)

    def test_ajax_articles_for_category(self):
        """Получение списка статей для категории Ajax-запросом"""
        self._populate_articles_for_category(self.categories[0])

        url = reverse('obed:article:category', kwargs={'section_category_slug': self.categories[0].slug})
        result = self.app.get(url, xhr=True)

        self.assertEqual(200, result.status_code)
        self.assertTemplateUsed(result, 'obed/article/article_list.html')
        self.assertEqual(3, len(result.context['object_list']))
        # NOTE: На данный момент пагинация используется постоянно. По умолчанию отдается 20 статей.
        self.assertIsNotNone(result.context['page_obj'])

    def test_ajax_articles_for_category_with_limit(self):
        """Получение списка статей для категории Ajax-запросом постранично"""
        self._populate_articles_for_category(self.categories[0])

        url = reverse('obed:article:category', kwargs={'section_category_slug': self.categories[0].slug})
        result = self.app.get(url, params={'limit': 2}, xhr=True)

        self.assertEqual(200, result.status_code)
        self.assertTemplateUsed(result, 'obed/article/article_list.html')
        self.assertEqual(2, len(result.context['object_list']))
        self.assertIsNotNone(result.context['page_obj'])

    def _populate_articles(self):
        for category in self.categories:
            create_material(
                'obed', 'article', section_category=category, site=self.site, sites=[self.site], is_hidden=False, n=3
            )
        create_material(
            'obed', 'article', section_category=self.categories[0], site=self.site, sites=[self.site], is_hidden=True,
        )

    def _populate_articles_for_category(self, category):
        create_material(
            'obed', 'article', section_category=category, site=self.site, sites=[self.site], is_hidden=False, n=3
        )
        create_material(
            'obed', 'article', section_category=category, site=self.site, sites=[self.site], is_hidden=True, n=3
        )
