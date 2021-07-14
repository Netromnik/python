# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import unittest

from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.news.models import News, Subject, Article, Video, Photo
from irk.options.models import Site

from irk.tests.unit_base import UnitTestBase

import unittest


class SubjectTestCase(UnitTestBase):
    """Сюжеты новостей"""

    def setUp(self):
        self._admin = self.create_user('admin', '123', is_admin=True)
        self._site = Site.objects.get(slugs='news')

    def test_index(self):
        """Индекс сюжетов"""

        G(Subject, n=5)
        response = self.app.get(reverse('news:subjects:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/subjects/index.html')
        self.assertEqual(len(response.context['objects']), 5)

    def test_read(self):
        """Страница сюжета"""

        subject = G(Subject)
        kwargs = {
            'subject': subject,
            'source_site': self._site,
        }

        main_materials = [
            self._create_material(Article, is_hidden=False, subject_main=True, **kwargs),
            self._create_material(Video, is_hidden=False, subject_main=True, **kwargs),
            self._create_material(Photo, is_hidden=True, subject_main=True, **kwargs),
        ]
        ribbon_materials = self._create_material(News, is_hidden=False, n=3, **kwargs)
        hidden_materials = self._create_material(News, is_hidden=True, n=2, **kwargs)

        url = reverse('news:subjects:read', kwargs={'slug': subject.slug})

        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/subjects/read.html')
        self.assertEqual(response.context['subject'].id, subject.id)
        self.assertEqual(2, len(response.context['main_materials']))
        self.assertEqual(3, len(response.context['ribbon_materials']))

        response = self.app.get(url, user=self._admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['subject'].id, subject.id)
        self.assertEqual(3, len(response.context['main_materials']))
        self.assertEqual(5, len(response.context['ribbon_materials']))

    @unittest.skip(u"В правой колонке больше не выводим похожие материалы")
    def test_read_other_materials(self):
        """
        Другие материалы на странице сюжета

        Другие материалы выбираются с помощью тегов по одному для каждого главного материала
        """

        subject = G(Subject)
        url = reverse('news:subjects:read', kwargs={'slug': subject.slug})
        kwargs = {
            'subject': subject,
            'source_site': self._site,
            'fill_nullable_fields': False,
        }

        main_1 = self._create_material(Article, is_hidden=False, subject_main=True, **kwargs)
        main_1.tags.add('test_1')
        main_2 = self._create_material(Photo, is_hidden=False, subject_main=True, **kwargs)
        main_2.tags.add('test_2')
        main_3 = self._create_material(Video, is_hidden=False, subject_main=True, **kwargs)
        main_3.tags.add('test_3')

        other_1 = self._create_material(Video, is_hidden=False, fill_nullable_fields=False)
        other_1.tags.add('test_1')
        other_2 = self._create_material(Photo, is_hidden=False, fill_nullable_fields=False)
        other_2.tags.add('test_2')
        other_3 = self._create_material(Article, is_hidden=False, fill_nullable_fields=False)
        other_3.tags.add('test_3')

        response = self.app.get(url)
        self.assertListEqual([other_1, other_2, other_3], response.context['other_materials'])

    def test_legacy_read(self):
        """Редирект сюжетов по старым урлам"""

        subject = G(Subject)
        response = self.app.get(reverse('news:subjects:read_legacy', args=(subject.slug, )))
        self.assertEqual(response.status_code, 301)  # Редирект
        response = response.follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/subjects/read.html')
        self.assertEqual(response.context['subject'].id, subject.id)

    def _create_material(self, model, **kwargs):
        """Создать материал с правильным определением content_type"""

        ct = ContentType.objects.get_for_model(model)

        return G(model, content_type=ct, **kwargs)