# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import random

from django.template import Template, Context

from django_dynamic_fixture import G

from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase, DummyRequest
from irk.news.models import ArticleType, Subject
from irk.news.templatetags.news_tags import similar_materials
from irk.news.tests.unit.material import create_material


class SidebarBlockTest(UnitTestBase):
    """Проверка вывода статей в блоках боковых колонок"""

    def test_header(self):
        """Шаблонный тег блока статей"""

        article_type_title = self.random_string(10)
        social_label = self.random_string(10)
        article_type = G(ArticleType, title=article_type_title, social_label=social_label)

        template = Template('''{% load news_tags %}{% news_sidebar_block 'article' limit=3 %}''')

        # Внутри раздела Новости
        site = Site.objects.get(slugs='news')
        create_material('news', 'article', type=article_type, is_hidden=False, sites=[site], site=site)
        setattr(site, 'site', site)

        result = template.render(Context({
            'request': DummyRequest(site=site),
        }))
        self.assertNotIn(article_type_title, result)


class SidebarBlockVideoTest(UnitTestBase):
    """Проверка вывода видео в блоках боковых колонок"""

    def setUp(self):
        self.site = Site.objects.get(slugs='news')
        setattr(self.site, 'site', self.site)

        self.request = DummyRequest()

    def test_not_display_video_older_one_week(self):
        """Видео добавленное больше чем неделю назад не должно выводиться"""

        template = Template('''{% load news_tags %}{% news_sidebar_block 'video' limit=1 %}''')

        video_title = self.random_string(10)
        create_material(
            'news', 'video', site=self.site, sites=[self.site], is_hidden=False, title=video_title,
            stamp=datetime.date.today() - datetime.timedelta(8)
        )

        result = template.render(Context({'request': self.request}))
        self.assertNotIn(video_title, result)

    def test_display_recent_video(self):
        """Видео добавленное меньше чем неделю назад должно выводиться"""

        template = Template('''{% load news_tags %}{% news_sidebar_block 'video' limit=1 %}''')

        video_title = self.random_string(10)
        create_material(
            'news', 'video', site=self.site, sites=[self.site], is_hidden=False, title=video_title,
            stamp=datetime.date.today()
        )
        result = template.render(Context({'request': self.request}))
        self.assertIn(video_title, result)


class SimilarMaterialTagTest(UnitTestBase):
    """Тесты для шаблонного тега похожих материалов"""

    def test_default(self):
        """
        По умолчанию выдает 3 лонгрида
        """

        subject = G(Subject)
        material = create_material('news', 'article', subject=subject, is_hidden=False)
        similar_longreads = self._create_longreads(subject=subject, is_hidden=False, n=5)
        self._create_longreads(subject=None, is_hidden=False, n=3)

        result = similar_materials(material)

        self.assertEqual(3, len(result))
        self.assertListContains([s.id for s in similar_longreads], [r.id for r in result])

    def test_with_limit(self):
        """
        Использование параметра limit
        """

        subject = G(Subject)
        material = create_material('news', 'news', subject=subject, is_hidden=False)
        similar_longreads = self._create_longreads(subject=subject, is_hidden=False, n=5)
        self._create_longreads(subject=subject, is_hidden=False, n=3)

        result = similar_materials(material, limit=4)

        self.assertEqual(4, len(result))
        self.assertListContains([s.id for s in similar_longreads], [r.id for r in result])

    def _create_longreads(self, **kwargs):
        """Создание связанных лонгридов"""

        model = random.choice(['video', 'photo', 'infographic'])

        stamp = datetime.datetime.now()
        kwargs.setdefault('stamp', stamp)

        return create_material('news', model, **kwargs)


class MaterialCardTagTest(UnitTestBase):
    """Тесты карточки материала"""

    def test_default(self):
        template = Template('''{% load news_tags %}{% material_card material %}''')

        title = self.random_string(10)
        material = create_material('news', 'video', is_hidden=False, title=title)

        context = Context({
            'material': material,
            'request': DummyRequest(),
        })

        result = template.render(context)
        self.assertIn(title, result)


class TildaTagTest(UnitTestBase):
    """Тесты для тегов, выводящих контент и ассеты тильдовских статей"""
