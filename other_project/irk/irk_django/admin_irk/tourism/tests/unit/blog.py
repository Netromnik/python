# -*- coding: utf-8 -*-

from __future__ import absolute_import
import datetime

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.phones.models import MetaSection
from irk.tests.unit_base import UnitTestBase


class TourismArticlesTestCase(UnitTestBase):
    """Тесты статей Туризма"""

    def setUp(self):
        super(TourismArticlesTestCase, self).setUp()
        self.site = Site.objects.get(slugs='tourism')
        self.date = datetime.date.today()
        self.admin = self.create_user('admin', '123', is_admin=True)
        G(MetaSection, id=2)  # Из левой колонки с меню

    def test_index(self):
        """Индекс статей"""

        create_material(
            'tourism', 'article', stamp=self.date, sites=[self.site, ], category=None, site=self.site, is_hidden=False,
            n=5
        )
        create_material(
            'tourism', 'article', stamp=self.date, sites=[self.site, ], category=None, site=self.site, is_hidden=True,
            n=2
        )
        response = self.app.get(reverse('tourism.views.article.index'))
        self.assertTemplateUsed(response, 'tourism/blog/index.html')
        self.assertEqual(5, len(response.context['objects']))

        response = self.app.get(reverse('tourism.views.article.index'), user=self.admin)
        self.assertEqual(7, len(response.context['objects']))

    def test_read(self):
        """Страница статьи"""

        slug = self.random_string(10).lower()
        article = create_material(
            'tourism', 'article', stamp=self.date, sites=[self.site, ], slug=slug, category=None, site=self.site,
            is_hidden=False
        )
        kwargs_ = {
            "year": self.date.year,
            "month": '%02d' % self.date.month,
            "day": '%02d' % self.date.day,
            "slug": slug
        }
        response = self.app.get(reverse('tourism.views.article.read', kwargs=kwargs_))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/blog/read.html')
        self.assertEqual(article, response.context['object'])

        article.is_hidden = True
        article.save()

        response = self.app.get(reverse('tourism.views.article.read', kwargs=kwargs_), status='*')
        self.assertEqual(response.status_code, 404)

        response = self.app.get(reverse('tourism.views.article.read', kwargs=kwargs_), user=self.admin)
        self.assertEqual(response.status_code, 200)
