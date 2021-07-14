# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
from django_dynamic_fixture import G, N

from django.core.urlresolvers import reverse

from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase

from irk.news.models import Article, Category
from irk.news.tests.unit.material import create_material


class ArticlesTestCase(UnitTestBase):
    """Тесты статей"""

    def setUp(self):
        super(ArticlesTestCase, self).setUp()
        self.date = datetime.date.today()
        self.admin = self.create_user('admin', '123', is_admin=True)
        self.site = Site.objects.get(slugs='news')

    def test_index(self):
        """Индекс статей"""

        create_material('news', 'article', stamp=self.date, category=None, is_hidden=False, n=5)
        create_material('news', 'article', stamp=self.date, category=None, is_hidden=True, n=2)
        response = self.app.get(reverse('news:article:index'))
        self.assertTemplateUsed(response, 'news-less/article/index.html')
        self.assertEqual(5, len(response.context['objects']))

        response = self.app.get(reverse('news:article:index'), user=self.admin)
        self.assertEqual(7, len(response.context['objects']))

    def test_ajax_index(self):
        """Индекс по ajax заросу"""

        create_material('news', 'article', stamp=self.date,category=None, is_hidden=False, n=5)
        response = self.app.get(reverse('news:article:index'), headers={'X_REQUESTED_WITH': 'XMLHttpRequest', })
        self.assertTemplateUsed(response, 'news-less/article/snippets/entries.html')
        self.assertEqual(5, len(response.context['objects']))

    def test_category(self):
        """Статьи по категории"""

        category = Category.objects.get(slug='culture')
        create_material(
            'news', 'article', stamp=self.date, site=self.site, sites=[self.site], category=category, is_hidden=False,
            n=5
        )
        create_material(
            'news', 'article', stamp=self.date, site=self.site, sites=[self.site], category=category, is_hidden=True,
            n=2
        )
        response = self.app.get(reverse('news:article:category', args=(category.slug, )))
        self.assertTemplateUsed(response, 'news-less/article/category.html')
        self.assertEqual(5, len(response.context['objects']))

        response = self.app.get(reverse('news:article:category', args=(category.slug, )), user=self.admin)
        self.assertEqual(7, len(response.context['objects']))

    def test_read(self):
        """Статья по алиасу"""

        slug = self.random_string(10).lower()
        article = create_material('news', 'article', stamp=self.date, slug=slug, category=None, is_hidden=False)
        kwargs_ = {
            "year": self.date.year,
            "month": '%02d' % self.date.month,
            "day": '%02d' % self.date.day,
            "slug": slug
        }
        response = self.app.get(reverse('news:article:read', kwargs=kwargs_))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/article/read.html')
        self.assertEqual(article, response.context['object'])

        article.is_hidden = True
        article.save()

        response = self.app.get(reverse('news:article:read', kwargs=kwargs_), status='*')
        self.assertEqual(response.status_code, 404)

        response = self.app.get(reverse('news:article:read', kwargs=kwargs_), user=self.admin)
        self.assertEqual(response.status_code, 200)


class ArticleModelTest(UnitTestBase):
    """Тесты для модели Article"""

    def test_fill_introduction(self):
        """Заполение поля «Введения» из текста статьи"""

        content_variants = [
            u'abc[intro]intro there[/intro]qwer',
            u'abc [intro]intro there[/intro]qwer',
            u'abc[intro]intro there[/intro] qwer',
            u'abc [intro]intro there[/intro] qwer',
        ]

        article = N(Article, content=self.random_text(500), introduction='')
        article.fill_introduction()
        self.assertFalse(article.introduction)

        for content in content_variants:
            article_with_intro = N(Article, content=content, introduction='')
            article_with_intro.fill_introduction()
            self.assertEqual(u'intro there', article_with_intro.introduction)
