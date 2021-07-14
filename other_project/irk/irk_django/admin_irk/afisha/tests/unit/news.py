# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.core.urlresolvers import reverse

from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase


class AfishaNewsTest(UnitTestBase):
    """Тестирование новостей афишы"""

    def test_news_index(self):
        """Открытие страницы новостей"""

        site = Site.objects.filter(slugs="afisha")[0]

        create_material(
            'news', 'news', n=10, sections=[site], slug=self.random_string(5).lower(), site=site, is_hidden=False,
            is_payed=False
        )

        response = self.app.get(reverse('afisha.news.index'))
        self.assertEquals(response.status_code, 200)

    def test_news_read(self):
        """Открытие страницы новости"""

        site = Site.objects.filter(slugs="afisha")[0]

        news = create_material(
            'news', 'news', n=1, sections=[site], slug=self.random_string(5).lower(), site=site, is_hidden=False,
            is_payed=False
        )

        response = self.app.get(
            reverse(
                'afisha.news.read',
                args=('%04d' % news.stamp.year, '%02d' % news.stamp.month, '%02d' % news.stamp.day, news.slug)
            )
        )
        self.assertEquals(response.status_code, 200)
