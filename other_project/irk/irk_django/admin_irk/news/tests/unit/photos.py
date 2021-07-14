# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime

from django.core.urlresolvers import reverse

from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase

from irk.news.tests.unit.material import create_material


class PhotoTestCase(UnitTestBase):
    """Тесты фоторепов"""

    def setUp(self):
        super(PhotoTestCase, self).setUp()
        self.news_site = Site.objects.get(slugs='news')
        self.afisha_site = Site.objects.get(slugs='afisha')
        self.admin = self.create_user('admin', 'admin', is_admin=True)
        self.user = self.create_user('user', 'user')

    def test_index(self):
        """Индекс фоторепов"""

        url = reverse('news:photo:index')
        # Проверяем вывод фоторепортажей
        create_material('news', 'photo', site=self.news_site, is_hidden=False, n=3)
        create_material('afisha', 'photo', site=self.afisha_site, is_hidden=False)

        response = self.app.get(url)
        self.assertTemplateUsed(response, 'news-less/photo/index.html')
        self.assertEqual(3, len(response.context['objects']))

        # Добавим еще один фоторепортаж и снова проверим, что он вывелся
        create_material('news', 'photo', site=self.news_site, is_hidden=False)

        context = self.app.get(url).context
        self.assertEqual(4, len(context['objects']))

        # Скрытые фоторепортажи не должны отображаться
        create_material('news', 'photo', site=self.news_site, is_hidden=True)

        context = self.app.get(url).context
        self.assertEqual(4, len(context['objects']))

        # Администратор должен видеть скрытые фоторепортажи
        context = self.app.get(url, user=self.admin).context
        self.assertEqual(5, len(context['objects']))

        # Фоторепортаж другого раздела не должен выводиться здесь
        create_material('news', 'photo', site=self.afisha_site, is_hidden=False)
        context = self.app.get(url, user=self.user).context
        self.assertEqual(4, len(context['objects']))

    def test_ajax_index(self):
        """Индекс по ajax заросу"""

        create_material('news', 'photo', site=self.news_site, is_hidden=False, n=5)
        response = self.app.get(reverse('news:photo:index'), headers={'X_REQUESTED_WITH': 'XMLHttpRequest', })
        self.assertTemplateUsed(response, 'news-less/photo/snippets/entries.html')
        self.assertEqual(5, len(response.context['objects']))

    def test_read(self):
        """Страница фоторепа"""

        today = datetime.datetime.today()
        slug = self.random_string(5).lower()

        photo = create_material('news', 'photo', stamp=today, slug=slug, site=self.news_site, is_hidden=False)
        create_material('news', 'photo', site=self.news_site, sites=[self.news_site], is_hidden=False,  n=2)
        afisha_photo = create_material(
            'afisha', 'photo', site=self.afisha_site, sites=[self.afisha_site], is_hidden=False
        )

        kwargs_ = {
            "year": today.year,
            "month": '%02d' % today.month,
            "day": '%02d' % today.day,
            "slug": slug
        }
        response = self.app.get(reverse('news:photo:read', kwargs=kwargs_))
        # Блок других фоторепов раздела
        self.assertEqual(2, len(response.context['other']))
        self.assertNotIn(afisha_photo, response.context['other'])

        photo.is_hidden = True
        photo.save()

        response = self.app.get(reverse('news:photo:read', kwargs=kwargs_), status='*')
        self.assertEqual(response.status_code, 404)

        response = self.app.get(reverse('news:photo:read', kwargs=kwargs_), user=self.admin)
        self.assertEqual(response.status_code, 200)
