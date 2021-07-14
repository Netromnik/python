# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime

from django.core.urlresolvers import reverse

from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase


class VideoTestCase(UnitTestBase):
    """Тесты видео"""

    def setUp(self):
        super(VideoTestCase, self).setUp()
        self.site = Site.objects.get(slugs='news')
        self.date = datetime.date.today()
        self.admin = self.create_user('admin', '123', is_admin=True)

    def test_index(self):
        """Индекс видео"""

        create_material('news', 'video', stamp=self.date, site=self.site, is_hidden=False, n=5)
        create_material('news', 'video', stamp=self.date, site=self.site, is_hidden=True, n=2)
        response = self.app.get(reverse('news:video:index'))
        self.assertTemplateUsed(response, 'news-less/video/index.html')
        self.assertEqual(5, len(response.context['objects']))

        response = self.app.get(reverse('news:video:index'), user=self.admin)
        self.assertEqual(7, len(response.context['objects']))

    def test_read(self):
        """Страница видео"""

        slug = self.random_string(10).lower()
        video = create_material('news', 'video', stamp=self.date, slug=slug, site=self.site, is_hidden=False)
        kwargs_ = {
            "year": self.date.year,
            "month": '%02d' % self.date.month,
            "day": '%02d' % self.date.day,
            "slug": slug
        }
        response = self.app.get(reverse('news:video:read', kwargs=kwargs_))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/video/read.html')
        self.assertEqual(video, response.context['object'])

        video.is_hidden = True
        video.save()

        response = self.app.get(reverse('news:video:read', kwargs=kwargs_), status='*')
        self.assertEqual(response.status_code, 404)

        response = self.app.get(reverse('news:video:read', kwargs=kwargs_), user=self.admin)
        self.assertEqual(response.status_code, 200)
