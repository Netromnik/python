# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
from PIL import Image

from django.conf import settings
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase

from irk.news.helpers import split_big_image
from irk.news.tests.unit.material import create_material


class InfographicTestCase(UnitTestBase):
    """Инфографика"""

    def test_index(self):
        """Главная инфографики"""

        objects = create_material('news', 'infographic', n=25, is_hidden=False)

        # Проверяем, что все записи вывелись на главной
        response = self.app.get('%s?page=3' % reverse('news:infographic:index'))

        self.assertTrue(isinstance(response.context['objects'].paginator, Paginator))
        self.assertEqual(len(response.context['objects'].object_list), 5)
        self.assertEqual(response.context['objects'].paginator.count, 25)

        for obj in objects[:20]:
            obj.is_hidden = True
            obj.save()

        response = self.app.get(reverse('news:infographic:index'))

        self.assertTemplateUsed(response, 'news-less/infographic/index.html')
        self.assertEqual(len(response.context['objects'].object_list), 5)
        self.assertEqual(response.context['objects'].paginator.count, 5)

    def test_paginator(self):
        """Пагинатор инфографики"""

        infographic = create_material('news', 'infographic', is_hidden=False)
        create_material('news', 'infographic', is_hidden=False, n=19)
        create_material('news', 'infographic', is_hidden=True, n=10)

        url = reverse('news:infographic:paginator')
        context = self.app.get(url).context
        self.assertTrue(isinstance(context['objects'].paginator, Paginator))
        self.assertEqual(len(context['objects'].object_list), 3)
        self.assertIn(infographic, context['objects'].object_list)
        self.assertEqual(context['objects'].paginator.count, 20)

        url = '%s?exclude_pk=%s' % (reverse('news:infographic:paginator'), infographic.pk)
        response = self.app.get(url)
        context = response.context
        self.assertTemplateUsed(response, 'news-less/infographic/entries.html')
        self.assertTrue(isinstance(context['objects'].paginator, Paginator))
        self.assertEqual(len(context['objects'].object_list), 3)
        self.assertNotIn(infographic, context['objects'].object_list)
        self.assertEqual(context['objects'].paginator.count, 19)


class BigInfographicTestCase(UnitTestBase):
    """Тестирование большой инфографики"""

    def test_read(self):
        """Страница инфографики"""

        image = Image.new("RGBA", size=(960, 9000), color=(256, 0, 0))
        full_path = os.path.join(settings.MEDIA_ROOT, 'big_infographic.png')
        image.save(full_path)

        split_big_image(full_path)

        infographic = create_material('news', 'infographic', is_hidden=False, image=full_path)
        url = reverse('news:infographic:read', args=(infographic.pk,))

        self.assertEqual(url, infographic.get_absolute_url())

        ipad_useragent = 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, ' \
                         'like Gecko) version/4.0.4 Mobile/7B367 Safari/531.21.10'
        desktop_useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu ' \
                            'Chromium/30.0.1599.114 Chrome/30.0.1599.114 Safari/537.36DNT: 1'

        response = self.app.get(url, headers={'User-Agent': desktop_useragent})
        self.assertTemplateUsed(response, 'news-less/infographic/read.html')
        self.assertEqual(response.context['object'], infographic)
        self.assertFalse(response.context['images'])

        response = self.app.get(url, headers={'User-Agent': ipad_useragent})
        self.assertEqual(response.context['object'], infographic)
        self.assertEqual(len(response.context['images']), 3)
        for image in response.context['images']:
            self.assertEqual(image['height'], 3000)
            self.assertEqual(image['width'], 960)

        infographic.is_hidden = True
        infographic.save()

        response = self.app.get(url, status=404)
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        super(BigInfographicTestCase, self).tearDown()
        # Удаляем нагенеренные в тесте файлы

        files = [f for f in os.listdir(settings.MEDIA_ROOT) if os.path.isfile(os.path.join(settings.MEDIA_ROOT, f))]
        for file_ in files:
            if file_.startswith('big_infographic'):
                os.remove(os.path.join(settings.MEDIA_ROOT, file_))
