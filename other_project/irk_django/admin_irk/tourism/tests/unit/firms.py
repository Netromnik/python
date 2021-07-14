# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.map.models import Cities as City
from irk.phones.models import MetaSection, Sections as Section
from irk.tests.unit_base import UnitTestBase

from irk.tourism.models import TourBase


class FirmsTestCase(UnitTestBase):
    """Тестирование фирм туризма"""

    csrf_checks = False

    def setUp(self):
        super(FirmsTestCase, self).setUp()
        G(MetaSection, id=2)
        ct = ContentType.objects.get_for_model(TourBase)
        self.section = G(Section, alias='bases', content_type=ct)
        self.user = self.create_user('vasya3')

    def test_firms_list(self):
        """Список фирм"""

        G(TourBase, section=[self.section, ], visible=True, n=4)
        G(TourBase, section=[self.section, ], visible=False, n=2)

        response = self.app.get(reverse('tourism:firm:section_firm_list', args=(self.section.slug, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/firm/list.html')
        self.assertEqual(len(response.context['objects'].object_list), 4)

    def test_firm_read(self):
        """Страница фирмы"""

        name = self.random_string(10)
        firm = G(TourBase, name=name, section=[self.section], visible=True)

        response = self.app.get(reverse('tourism.views.firms.section_firm', args=(self.section.slug, firm.id)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/firm/read.html')
        self.assertEqual(response.context['object'].name, name)

    def test_firm_create(self):
        """Создать фирму"""

        url = reverse('tourism:firm:create', args=(self.section.slug, ))
        response = self.app.get(url)
        self.assertEqual(response.status_code, 302)  # редирект для неавторизованных

        response = self.app.get(url, user=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/firm/create.html')

        name = self.random_string(10)
        params = {
            'name': name,
            'models': 'tourbase',
            'address_set-0-city_id': City.objects.get(alias='irkutsk').id,
            'address_set-TOTAL_FORMS': 1,
            'address_set-INITIAL_FORMS': 0,
            'address_set-MAX_NUM_FORMS': 10,
            'gallerypicture_set-TOTAL_FORMS': 48,
            'gallerypicture_set-INITIAL_FORMS': 0,
            'gallerypicture_set-MAX_NUM_FORMS': 48,
        }
        response = self.app.post(url, params, user=self.user)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/firm/created.html')
        self.assertEqual(TourBase.objects.filter(name=name).exists(), True)

    def test_firm_update(self):
        """Отредактировать фирму"""

        firm = G(TourBase, section=[self.section, ], visible=True, user=self.user)
        url = reverse('tourism.views.firms.edit_firm', args=(self.section.slug, firm.id))

        response = self.app.get(url)
        self.assertEqual(response.status_code, 302)  # левых юзеров лесом

        response = self.app.get(url, user=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/firm/edit.html')

        name = self.random_string(10)
        params = {
            'name': name,
            'models': 'tourbase',
            'address_set-0-city_id': City.objects.get(alias='irkutsk').id,
            'address_set-TOTAL_FORMS': 1,
            'address_set-INITIAL_FORMS': 0,
            'address_set-MAX_NUM_FORMS': 10,
            'gallerypicture_set-TOTAL_FORMS': 48,
            'gallerypicture_set-INITIAL_FORMS': 0,
            'gallerypicture_set-MAX_NUM_FORMS': 48,
        }
        old_name = firm.name
        response = self.app.post(url, params, user=self.user).follow()
        self.assertEquals(response.status_code, 200)

        new_name = TourBase.objects.get(id=firm.id).name
        self.assertEqual(new_name, name)
        self.assertNotEqual(new_name, old_name)

    def test_firm_update_for_authorized_user(self):
        """Авторизованный пользователь не относящийся к фирме не может его редактировать"""

        firm = G(TourBase, section=[self.section, ], visible=True, user=self.user)
        url = reverse('tourism.views.firms.edit_firm', args=(self.section.slug, firm.id))

        hacker = self.create_user('hacker')

        response = self.app.get(url, user=hacker, expect_errors=True)
        self.assertEqual(response.status_code, 403)
