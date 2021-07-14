# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.options.models import Site
from irk.phones.models import MetaSection
from irk.tests.unit_base import UnitTestBase
from irk.news.tests.unit.material import create_material


class TourismNewsTest(UnitTestBase):
    """Тестирование новостей туризма"""

    def setUp(self):
        super(TourismNewsTest, self).setUp()
        G(MetaSection, id=2)
        self.site = Site.objects.get(slugs="tourism")
        self.admin = self.create_user('admin', '123', is_admin=True)
        self.stamp = datetime.date.today()

    def test_index(self):
        """Индекс новостей"""

        create_material('tourism', 'news', sites=[self.site, ], site=self.site, is_hidden=False, n=5)
        create_material('tourism', 'news', sites=[self.site, ], site=self.site, is_hidden=True, n=2)

        response = self.app.get(reverse('tourism:news:index'))
        self.assertTemplateUsed(response, 'tourism/news/index.html')
        self.assertEqual(5, len(response.context['objects']))

        response = self.app.get(reverse('tourism:news:index'), user=self.admin)
        self.assertEqual(7, len(response.context['objects']))

    def test_read(self):
        """Страница новости"""

        slug = self.random_string(10).lower()
        news = create_material(
            'tourism', 'news', slug=slug, sites=[self.site, ], stamp=self.stamp, site=self.site, is_hidden=False
        )
        kwargs_ = {
            "year": self.stamp.year,
            "month": '%02d' % self.stamp.month,
            "day": '%02d' % self.stamp.day,
            "slug": slug,
        }
        response = self.app.get(reverse('tourism.news.read', kwargs=kwargs_))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/news/read.html')
        self.assertEqual(news, response.context['object'])

        news.is_hidden = True
        news.save()

        response = self.app.get(reverse('tourism.news.read', kwargs=kwargs_), status='*')
        self.assertEqual(response.status_code, 404)

        response = self.app.get(reverse('tourism.news.read', kwargs=kwargs_), user=self.admin)
        self.assertEqual(response.status_code, 200)
