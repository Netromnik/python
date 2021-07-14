# -*- coding: utf-8 -*-

import datetime
import random
import json
import mock

from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase
from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.map.models import Cities as City

from irk.home import settings as app_settings


class MaterialTestCase(UnitTestBase):
    """ Материалы на главной странице """

    def setUp(self):
        self.home_site = Site.objects.get(slugs='home')
        self.news_site = Site.objects.get(slugs='news')
        self.city_irkutsk = City.objects.get(alias='irkutsk')
        self.admin = self.create_user('admin', 'admin', is_admin=True)
        self.url = reverse('home_index')

    def _get_materials(self, user=None):
        return self.app.get(self.url, user=user).context['materials']

    def test_materials(self):
        """Список материалов на главной"""

        today = datetime.date.today()
        kwargs = {
            'sites': [self.home_site, ],
            'is_hidden': False,
            'stamp': today,
            'published_time': datetime.datetime.now().time(),
            'site': self.news_site,
            'last_comment': None,
            'fill_nullable_fields': False,
        }

        for model in ('photo', 'infographic', 'video', 'article'):
            create_material('news', model, n=6, **kwargs)

        materials = self._get_materials()
        self.assertEqual(app_settings.HOME_POSITIONS_COUNT, len(materials))

        # Скрытые материалы доступны только админам
        kwargs['is_hidden'] = True
        hidden_material = create_material('news', 'video', **kwargs)

        # Анонимы и пользователи не видят скрытые
        materials = self._get_materials()
        self.assertNotEqual(materials[0], hidden_material)

        # Админы видят скрытые (но не дальше FUTURE_WINDOW)
        materials = self._get_materials(user=self.admin)
        self.assertEqual(materials[0], hidden_material)

    def test_sites(self):
        """Тестирование привязки новостей к главной странице"""

        today = datetime.date.today()
        filters = {
            'sites': [self.news_site, ],
            'is_hidden': False,
            'stamp': today,
            'site': self.news_site,
            'last_comment': None,
            'fill_nullable_fields': False,
        }

        # Новости не привязанные к главной не выводятся
        for model in ('photo', 'infographic', 'video', 'article'):
            create_material('news', model, n=5, **filters)
        self.assertEqual(0, len(self._get_materials()))

        # Новости привязанные к главной выводятся
        filters['sites'] = [self.home_site, ]
        for model in ('photo', 'infographic', 'video', 'article'):
            create_material('news', model, n=6, **filters)
        self.assertEqual(app_settings.HOME_POSITIONS_COUNT, len(self._get_materials()))

    def test_sticked_hidden_not_show_for_user(self):
        """Проверка, что скрытые закрепленные материалы не видны пользователям."""

        today = datetime.date.today()

        kwargs = {
            'sites': [self.home_site, ],
            'is_hidden': True,
            'stamp': today,
            'site': self.news_site,
            'last_comment': None,
            'fill_nullable_fields': False,
        }

        # Закрепленные материалы
        sticked_material_1 = create_material('news', 'article', stick_position=2, **kwargs)
        sticked_material_2 = create_material('news', 'article', stick_position=7, **kwargs)

        # Обычный пользователь не видит скрытых закрепленных материалов
        materials = self._get_materials()
        self.assertNotIn(sticked_material_1, materials)
        self.assertNotIn(sticked_material_2, materials)

        # Модератор же их видит
        materials = self._get_materials(user=self.admin)
        self.assertIn(sticked_material_1, materials)
        self.assertIn(sticked_material_2, materials)

    def test_sticked_materials(self):
        """Проверка закрепления материалов"""

        kwargs = {
            'sites': [self.home_site, ],
            'is_hidden': False,
            'stamp': datetime.date.today(),
            'site': self.news_site,
            'last_comment': None,
            'fill_nullable_fields': False,
        }
        initial_materials = []
        for model in ('photo', 'infographic', 'video', 'article'):
            initial_materials.extend(create_material('news', model, n=5, **kwargs))

        stick_material = initial_materials[13]
        stick_material.set_stick_position(3, save=True)

        materials = self._get_materials()
        self.assertEqual(stick_material, materials[2])

        # Вышел новый материал, закрепленный остался на месте
        recent_material = create_material('news', 'article', **kwargs)

        materials = self._get_materials()
        self.assertEqual(recent_material, materials[0])
        self.assertEqual(stick_material, materials[2])


class MaterialPositionsAdminTest(UnitTestBase):
    """Тесты страницы в админке Расположение материалов"""

    csrf_checks = False

    def setUp(self):
        self._home_site = Site.objects.get(slugs='home')
        self._news_site = Site.objects.get(slugs='news')
        self._city_irkutsk = City.objects.get(alias='irkutsk')
        self._admin = self.create_user('admin', 'admin', is_admin=True)
        self._hacker = self.create_user('Neo')
        self._url = reverse('admin_material_home_positions')
        self._url_save = reverse('admin_material_home_positions_save')
        self._limit = app_settings.HOME_POSITIONS_COUNT

    def _populate(self):
        kwargs = {
            'sites': [self._home_site, ],
            'is_hidden': False,
            'stamp': datetime.date.today(),
            'site': self._news_site,
            'last_comment': None,
            'fill_nullable_fields': False,
        }
        self._initial_materials = []
        for model in ('photo', 'infographic', 'video', 'article'):
            self._initial_materials.extend(create_material('news', model, n=6, **kwargs))

    def _get_materials(self):
        """Получить материалы"""

        response = self.app.get(self._url, user=self._admin)

        return response.context['main_materials']

    def _ajax(self, url, data, user):
        """Отправить ajax запрос на сервер"""

        return self.app.post(
            url, params=json.dumps(data), content_type='application/json', user=user, xhr=True, expect_errors=True
        )

    def test_success(self):
        """Проверка изменения списка материалов"""

        self._populate()
        materials = self._get_materials()
        # Пересортируем материалы
        random.shuffle(materials)
        post_data = {
            'materials': [
                {'id': m.pk, 'stick_position': None}
                for m in materials
            ]
        }

        response = self._ajax(self._url_save, post_data, self._admin)
        self.assertStatusIsOk(response)
        self.assertTrue(response.json['ok'])

        self.assertItemsEqual(materials, self._get_materials())

    def test_access_denied(self):
        """Доступ только редакторам новостей. Сохранение через AJAX"""

        # У пользователя нет прав
        response = self.app.get(self._url, user=self._hacker, expect_errors=True)
        self.assertIn(response.status_code, (302, 403))

        # У пользователя нет прав
        response = self._ajax(self._url_save, {}, user=self._hacker)
        self.assertEqual(403, response.status_code)

        # Не ajax запрос
        response = self.app.post(self._url_save, '{}', user=self._admin, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_stick_position(self):
        """Закрепление материалов"""

        self._populate()
        materials = self._get_materials()
        post_data = {
            'materials': [
                {'id': m.pk, 'stick_position': None} for m in materials
            ]
        }

        # Первый материал закрепляем на 4 позиции (отсчет с 0)
        sticked_material_1 = materials[0]
        post_data['materials'][0]['stick_position'] = 3
        # Второй материал закрепляем на 8 позиции (отсчет с 0)
        sticked_material_2 = materials[1]
        post_data['materials'][1]['stick_position'] = 7

        response = self._ajax(self._url_save, post_data, self._admin)
        self.assertTrue(response.json['ok'])

        result_materials = self._get_materials()
        self.assertEqual(sticked_material_1, result_materials[2])
        self.assertEqual(sticked_material_2, result_materials[6])

    def test_invalid_id(self):
        """Недействительный идентификатор материала"""
        self._populate()
        materials = self._get_materials()
        post_data = {
            'materials': [
                {'id': m.pk, 'stick_position': None}
                for m in materials
            ]
        }
        post_data['materials'][5]['id'] = 'invalid'

        response = self._ajax(self._url_save, post_data, self._admin)
        self.assertFalse(response.json['ok'])

    @mock.patch('irk.news.admin_views.BaseMaterial.material_objects.get')
    def test_unknown_error(self, get):
        """Неизвестная ошибка"""

        get.side_effect = Exception('Boom!')
        self._populate()
        materials = self._get_materials()
        post_data = {
            'materials': [
                {'id': m.pk, 'stick_position': None}
                for m in materials
            ]
        }

        response = self._ajax(self._url_save, post_data, self._admin)
        self.assertFalse(response.json['ok'])
        self.assertEqual('Boom!', response.json['error'])
