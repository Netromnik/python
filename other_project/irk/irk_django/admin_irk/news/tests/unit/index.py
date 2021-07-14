# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
from django_dynamic_fixture import G

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from irk.news.models import Article, News, Infographic, Photo, Video, Block, Category
from irk.news.helpers import clear_cache, MaterialController
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase


class IndexViewTest(UnitTestBase):
    """Тесты главной страницы раздела Новости"""

    def setUp(self):
        self.url = reverse('news:index')
        self.site = Site.objects.get(slugs='news')
        self.admin = self.create_user('admin', '123', is_admin=True)
        self.material_controller = MaterialController()

        # Очистка кэша материалов Redis
        clear_cache()

    def tearDown(self):
        # Очистка кэша материалов Redis
        clear_cache()

    def test_template_and_context(self):
        """Проверка используемого шаблона и наличия необходимых переменных контекста"""

        response = self.app.get(self.url)

        self.assertTemplateUsed(response, 'news-less/index.html')
        self.assertIn('super_material', response.context)
        self.assertIn('ribbon_materials', response.context)
        self.assertIn('is_moderator', response.context)
        self.assertIn('important_materials', response.context)
        self.assertIn('sidebar_materials', response.context)

    def test_ribbon_materials(self):
        """
        Проверка отображения материалов в ленте.

        Отображается 20 материалов в хронологическом порядке.
        """

        common_kwargs = {
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False
        }

        self._create_material(Article, n=5, **common_kwargs)
        self._create_material(News, n=10, **common_kwargs)
        self._create_material(Video, n=3, **common_kwargs)
        self._create_material(Infographic, n=2, **common_kwargs)
        self.material_controller.pregenerate_cache()

        response = self.app.get(self.url)

        self.assertEqual(20, len(response.context['ribbon_materials']))

    def test_not_hidden_into_ribbon_materials(self):
        """Скрытые материалы в ленте отображается только для редакторов"""

        self._create_material(Article, source_site=self.site, sites=[self.site], is_hidden=False, n=5)
        self._create_material(News, source_site=self.site, sites=[self.site], is_hidden=False, n=10)
        self._create_material(News, source_site=self.site, sites=[self.site], is_hidden=True, n=5)
        self.material_controller.pregenerate_cache()

        response = self.app.get(self.url)

        self.assertEqual(15, len(response.context['ribbon_materials']))

        response = self.app.get(self.url, user=self.admin)

        self.assertEqual(20, len(response.context['ribbon_materials']))

    def test_not_advertising_into_ribbon_materials(self):
        """Рекламные не попадают в ленту"""

        common_kwargs = {
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False
        }

        self._create_material(News, n=10, **common_kwargs)
        self._create_material(Article, n=5, **common_kwargs)
        advertising_materials = [
            self._create_material(News, is_advertising=True, **common_kwargs),
            self._create_material(Article, is_advertising=True, **common_kwargs),
            self._create_material(Photo, is_advertising=True, **common_kwargs),
            self._create_material(Video, is_advertising=True, **common_kwargs),
            self._create_material(Infographic, is_advertising=True, **common_kwargs),
        ]
        self.material_controller.pregenerate_cache()

        response = self.app.get(self.url)

        self.assertEqual(15, len(response.context['ribbon_materials']))
        self.assertListNotContains(response.context['ribbon_materials'], advertising_materials)

    def test_super_material(self):
        """Проверка супер-материала"""

        article = self._create_material(Article, is_super=True, is_hidden=False)

        response = self.app.get(self.url)

        self.assertEqual(article, response.context['super_material'])

    def test_not_super_into_ribbon_materials(self):
        """супер-материал не попадает в ленту"""

        common_kwargs = {
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False
        }

        self._create_material(News, n=10, **common_kwargs)
        self._create_material(Article, n=5, **common_kwargs)
        super_material = self._create_material(Article, is_super=True, **common_kwargs)

        response = self.app.get(self.url)

        self.assertNotIn(super_material, response.context['ribbon_materials'])

    def test_important_materials(self):
        """
        Проверка материалов в блоке «Главное».

        Отображается максимум 3 материала. Сортировка по дате публикации.
        """

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        common_kwargs = {
            'is_important': True,
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False,
        }

        article = self._create_material(Article, stamp=today, **common_kwargs)
        news = self._create_material(News, stamp=today, **common_kwargs)
        video = self._create_material(Video, stamp=yesterday, **common_kwargs)
        info = self._create_material(Infographic, stamp=today, **common_kwargs)
        self.material_controller.pregenerate_cache()

        response = self.app.get(self.url)

        self.assertEqual(3, len(response.context['important_materials']))
        self.assertListContains(response.context['important_materials'], [news, article, info])
        self.assertNotIn(video, response.context['important_materials'])

    def test_super_into_ribbon_materials(self):
        """Супер-материал может выводиться в блоке «Главное»"""

        common_kwargs = {
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False,
            'is_important': True,
        }

        super_material = self._create_material(Article, is_super=True, **common_kwargs)
        news = self._create_material(News, **common_kwargs)
        video = self._create_material(Video, **common_kwargs)
        self.material_controller.pregenerate_cache()

        response = self.app.get(self.url)

        self.assertListContains(response.context['important_materials'], [news, super_material, video])

    def test_sidebar_materials(self):
        """
        Проверка материалов в боковой колонке.

        Выводится 4 (а если нет баннера, то 5) материалов, привязанных к этому блоку через админку.
        Для каждого материала указывается свой номер позиции в блоке.
        """

        # NOTE: не понятно как тестировать наличие/отсутствие баннера

        block = Block.objects.get(slug='news_index_sidebar')

        article = self._create_material(Article, source_site=self.site, is_hidden=False)
        news = self._create_material(News, source_site=self.site, is_hidden=False)
        video = self._create_material(Video, source_site=self.site, is_hidden=False)
        info = self._create_material(Infographic, source_site=self.site, is_hidden=False)

        block.positions.create(material=article, number=1)
        block.positions.create(material=news, number=3)
        block.positions.create(material=video, number=2)
        block.positions.create(material=info, number=4)

        response = self.app.get(self.url)

        self.assertListEqual([article, video, news, info], response.context['sidebar_materials'])

    def _create_material(self, model, **kwargs):
        """Создать материал с правильным определением content_type"""

        ct = ContentType.objects.get_for_model(model)

        return G(model, content_type=ct, **kwargs)


class ArchiveViewTest(UnitTestBase):
    """Тесты архива материалов"""

    def setUp(self):
        self.site = Site.objects.get(slugs='news')
        self.admin = self.create_user('admin', '123', is_admin=True)
        self.today = datetime.date.today()
        self.material_controller = MaterialController()

        # Очистка кэша материалов Redis
        clear_cache()

    def test_template_and_context(self):
        """Проверка используемого шаблона и наличия необходимых переменных контекста"""

        response = self.app.get(self._get_archive_url(self.today))

        self.assertTemplateUsed(response, 'news-less/index.html')
        self.assertIn('ribbon_materials', response.context)
        self.assertIn('is_moderator', response.context)
        self.assertIn('important_materials', response.context)
        self.assertIn('sidebar_materials', response.context)

    def test_ribbon_materials(self):
        """
        Проверка отображения материалов в ленте.

        Отображаются все материалы на конкретную дату (35 материалов для теста).
        """

        common_kwargs = {
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False
        }

        date = self.today - datetime.timedelta(days=30)

        self._create_material(Article, stamp=date, n=10, **common_kwargs)
        self._create_material(News, stamp=date, n=15, **common_kwargs)
        self._create_material(News, stamp=self.today, n=10, **common_kwargs)
        self._create_material(Video, stamp=date, n=5, **common_kwargs)
        self._create_material(Infographic, stamp=date, n=5, **common_kwargs)
        self.material_controller.pregenerate_cache()

        response = self.app.get(self._get_archive_url(date))

        self.assertEqual(35, len(response.context['ribbon_materials']))

    def test_ribbon_materials_when_hidden(self):
        """Скрытые материалы отображаются только модераторам."""

        common_kwargs = {
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False
        }

        date = self.today - datetime.timedelta(days=30)

        self._create_material(Article, source_site=self.site, sites=[self.site], is_hidden=True, stamp=date, n=10)
        self._create_material(News, stamp=date, n=15, **common_kwargs)
        self._create_material(News, stamp=self.today, n=10, **common_kwargs)
        self._create_material(Video, stamp=date, n=5, **common_kwargs)
        self._create_material(Infographic, stamp=date, n=5, **common_kwargs)
        self.material_controller.pregenerate_cache()

        response = self.app.get(self._get_archive_url(date))

        self.assertEqual(25, len(response.context['ribbon_materials']))

        response = self.app.get(self._get_archive_url(date), user=self.admin)

        self.assertEqual(35, len(response.context['ribbon_materials']))

    def _get_archive_url(self, date):
        """Получить url для архива на конкретную дату"""

        return reverse('news:news:date', args=u'{:%Y %m %d}'.format(date).split())

    def _create_material(self, model, **kwargs):
        """Создать материал с правильным определением content_type"""

        ct = ContentType.objects.get_for_model(model)

        return G(model, content_type=ct, **kwargs)


class RubricViewTest(UnitTestBase):
    """Тесты для страницы материалов конкретной рубрики"""

    def setUp(self):
        self.site = Site.objects.get(slugs='news')
        self.admin = self.create_user('admin', '123', is_admin=True)
        self.material_controller = MaterialController()

        # Очистка кэша материалов Redis
        clear_cache()

    def test_template_and_context(self):
        """Проверка используемого шаблона и наличия необходимых переменных контекста"""

        category = G(Category)

        response = self.app.get(self._get_rubric_url(category.slug))

        self.assertTemplateUsed(response, 'news-less/index.html')
        self.assertIn('ribbon_materials', response.context)
        self.assertIn('is_moderator', response.context)
        self.assertIn('important_materials', response.context)
        self.assertIn('sidebar_materials', response.context)

    def test_when_category_not_exist(self):
        """Категория не существует"""

        response = self.app.get(self._get_rubric_url('fake'), status='*')

        self.assertEqual(404, response.status_code)

    def test_ribbon_materials(self):
        category = G(Category)

        common_kwargs = {
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False,
        }

        self._create_material(Article, n=10, category=category, **common_kwargs)
        self._create_material(News, n=15, category=category, **common_kwargs)
        self._create_material(Photo, n=10, category=category, **common_kwargs)
        self._create_material(Video, n=5, category=category, **common_kwargs)
        self._create_material(Infographic, n=5, category=category, **common_kwargs)
        self.material_controller.save_ribbon_materials_for_category_first_page(category.slug)

        response = self.app.get(self._get_rubric_url(category.slug))

        self.assertEqual(20, len(response.context['ribbon_materials']))

    def test_sidebar_materials(self):
        """
        Материалы в правой колонке.

        Отображаются 4 последних лонгрида для рубрики.
        """

        common_kwargs = {
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False,
        }

        category = G(Category)
        longrids = [
            self._create_material(Article, category=category, **common_kwargs),
            self._create_material(Photo, category=category, **common_kwargs),
            self._create_material(Video, category=category, **common_kwargs),
            self._create_material(Video, category=category, **common_kwargs),
            self._create_material(Infographic, category=category, **common_kwargs),
            self._create_material(Infographic, category=category, **common_kwargs),
        ]
        non_longrids = [
            self._create_material(News, category=category, **common_kwargs),
        ]

        other_category = [
            self._create_material(Article, **common_kwargs),
            self._create_material(Photo, **common_kwargs),
            self._create_material(Video, **common_kwargs),
            self._create_material(Infographic, **common_kwargs),
        ]
        self.material_controller.save_last_longrid_materials_for_category(category.slug)

        response = self.app.get(self._get_rubric_url(category.slug))

        self.assertEqual(4, len(response.context['sidebar_materials']))
        self.assertListNotContains(response.context['sidebar_materials'], non_longrids)
        self.assertListNotContains(response.context['sidebar_materials'], other_category)

    def test_not_advertising_into_sidebar_materials(self):
        """Рекламные не попадают в блок в правой колонке"""

        category = G(Category)

        common_kwargs = {
            'category': category,
            'source_site': self.site,
            'sites': [self.site],
            'is_hidden': False,
        }

        materials = [
            self._create_material(Article, **common_kwargs),
            self._create_material(Photo, **common_kwargs),
        ]
        advertising_materials = [
            self._create_material(Article, is_advertising=True, **common_kwargs),
            self._create_material(Photo, is_advertising=True, **common_kwargs)
        ]
        self.material_controller.save_last_longrid_materials_for_category(category.slug)

        response = self.app.get(self._get_rubric_url(category.slug))

        self.assertEqual(2, len(response.context['sidebar_materials']))
        self.assertListContains(response.context['sidebar_materials'], materials)
        self.assertListNotContains(response.context['sidebar_materials'], advertising_materials)

    def _get_rubric_url(self, slug):
        """Получить url для рубрики/категории"""

        return reverse('news:news_type', kwargs={'slug': slug})

    def _create_material(self, model, **kwargs):
        """Создать материал с правильным определением content_type"""

        ct = ContentType.objects.get_for_model(model)

        return G(model, content_type=ct, **kwargs)
