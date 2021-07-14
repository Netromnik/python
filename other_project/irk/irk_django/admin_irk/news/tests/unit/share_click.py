# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django_dynamic_fixture import G

from django.core.urlresolvers import reverse

from irk.news.models import News
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase


class ShareClickViewTest(UnitTestBase):
    """Тест статистики кликов по соц. кнопкам у материалов"""

    csrf_checks = False

    def setUp(self):
        self.site = Site.objects.get(slugs='news')

    def _get_share_cnt(self, material, slug):
        material = News.objects.get(pk=material.pk)
        field_name = '{}_share_cnt'.format(slug)
        return getattr(material, field_name)

    def test_click_share(self):
        """Тест статистики кликов по соц. кнопкам у материалов"""

        material = G(News, source_site=self.site, sites=[self.site], is_hidden=False)

        url = reverse('news:share_click', kwargs={'pk': material.pk, 'slug': 'ok1'})
        response = self.app.post(url, status=404)
        self.assertEqual(response.status_code, 404)

        url = reverse('news:share_click', kwargs={'pk': material.pk, 'slug': 'ok1'})
        response = self.app.get(url, status=405, xhr=True)
        self.assertEqual(response.status_code, 405)

        url = reverse('news:share_click', kwargs={'pk': material.pk, 'slug': 'ok1'})
        response = self.app.post(url, status=404, xhr=True)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(self._get_share_cnt(material, 'vk'), 0)
        self.assertEqual(self._get_share_cnt(material, 'ok'), 0)
        self.assertEqual(self._get_share_cnt(material, 'fb'), 0)
        self.assertEqual(self._get_share_cnt(material, 'tw'), 0)

        url = reverse('news:share_click', kwargs={'pk': material.pk, 'slug': 'ok'})
        response = self.app.post(url, status=200, xhr=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._get_share_cnt(material, 'vk'), 0)
        self.assertEqual(self._get_share_cnt(material, 'ok'), 1)
        self.assertEqual(self._get_share_cnt(material, 'fb'), 0)
        self.assertEqual(self._get_share_cnt(material, 'tw'), 0)

        url = reverse('news:share_click', kwargs={'pk': material.pk, 'slug': 'vk'})
        self.app.post(url, xhr=True)
        self.app.post(url, xhr=True)
        self.assertEqual(self._get_share_cnt(material, 'vk'), 2)
