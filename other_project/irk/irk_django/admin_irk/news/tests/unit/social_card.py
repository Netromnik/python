# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django_dynamic_fixture import G

from irk.news.models import ArticleType
from irk.news.tests.unit.material import create_material
from irk.obed.models import ArticleCategory
from irk.special.models import Project
from irk.tests.unit_base import UnitTestBase


class SocialCardTest(UnitTestBase):
    """Тесты социальных карточек"""

    materials = {
        ('news', 'news'): u'Новости',
        ('news', 'photo'): u'Фоторепортажи',
        ('news', 'video'): u'Видео',
        ('news', 'infographic'): u'Инфографика',
        ('news', 'test'): u'Тесты',
        ('afisha', 'photo'): u'Фоторепортажи',
        ('afisha', 'poll'): u'Опросы',
        ('afisha', 'test'): u'Тесты',
        ('obed', 'poll'): u'Опросы',
        ('obed', 'test'): u'Тесты',
        ('tourism', 'news'): u'Новости',
        ('tourism', 'infographic'): u'Инфографика',
        ('tourism', 'poll'): u'Опросы',
        ('currency', 'news'): u'Новости',
        ('experts', 'expert'): u'Эксперт',
        ('contests', 'contest'): u'Конкурсы',
    }

    def setUp(self):
        self._article_type = G(ArticleType, social_label='Статьи')

    def test_materials(self):
        """Формирование меток для социальных карточек материалов"""

        for (app_label, model), label in self.materials.items():
            material = create_material(app_label, model, project=None, social_label='')
            self.assertEqual(
                label, material.get_social_label(), 'Failed {}_{}: {} != {}'.format(
                    app_label, model, label, material.get_social_label()
                )
            )

    def test_article_types(self):
        """Метки для статей различных типов"""

        article_types = ['Статьи', 'Рецензии', 'Обзоры', 'Интервью', 'Репортажи', 'Комментарии']

        for at in article_types:
            article_type = G(ArticleType, social_label=at)
            article = create_material('news', 'article', type=article_type, project=None, social_label='')
            self.assertEqual(at, article.get_social_label(), 'Failed {} != {}'.format(at, article.get_social_label()))

    def test_projects(self):
        """Метки материалов из спецпроектов"""

        projects = [
            'Ресторанный обозреватель', 'Любимое дело', 'Джаз на Байкале', 'Клуб путешественников', 'День Победы',
            'Хорошо там, где мы есть', 'Семейный архив', 'Коллекции иркутян', 'Как это устроено?', 'Азбука Иркутска',
            'Политика в вопросах и ответах', 'Книги и приключения'
        ]

        for title in projects:
            project = G(Project, title=title)
            material = create_material('news', 'article', project=project, type=self._article_type, social_label='')
            self.assertEqual(
                title, material.get_social_label(), 'Failed {} != {}'.format(title, material.get_social_label())
            )

    def test_obed_articles(self):
        """Метки статей из обеда"""

        categories = {
            ('delicious', 'Справочник'): 'Статьи',
            ('critic', 'Ресторанный обозреватель'): 'Ресторанный обозреватель',
            ('recipe', 'Рецепты'): 'Рецепты',
            ('list', 'Лента «Обеда»'): 'Статьи',
        }

        for (slug, title), label in categories.items():
            category = G(ArticleCategory, slug=slug, title=title)
            article = create_material(
                'obed', 'article', section_category=category, project=None, type=self._article_type, social_label=''
            )
            self.assertEqual(
                label, article.get_social_label(), 'Failed {} != {}'.format(label, article.get_social_label())
            )
