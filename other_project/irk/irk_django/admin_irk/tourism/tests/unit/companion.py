# -*- coding: utf-8 -*-
from __future__ import absolute_import

from urllib import urlencode

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.tourism.models import Companion

from irk.phones.models import MetaSection
from irk.tests.unit_base import UnitTestBase


class CompanionTest(UnitTestBase):
    """Поиск попутчика в Туризме"""

    csrf_checks = False

    def setUp(self):
        super(CompanionTest, self).setUp()
        G(MetaSection, id=2)
        self.user = self.create_user('user', '123')
        self.evil_user = self.create_user('evil_user', '123')

    def test_read_companion(self):
        """Страница компаньона"""

        companion_t_e = G(Companion, visible=True, author=self.evil_user)
        companion_t_u = G(Companion, visible=True, author=self.user)
        companion_f_e = G(Companion, visible=False, author=self.evil_user)
        companion_f_u = G(Companion, visible=False, author=self.user)

        response = self.app.get(reverse('tourism:companion:read', args=(companion_t_e.pk,)))
        self.assertTemplateUsed(response, 'tourism/companion/read.html')
        self.assertEqual(response.context['companion'], companion_t_e)
        response = self.app.get(reverse('tourism:companion:read', args=(companion_t_u.pk,)))
        self.assertEqual(response.context['companion'], companion_t_u)
        response = self.app.get(reverse('tourism:companion:read', args=(companion_f_e.pk,)),
                                expect_errors=True)
        self.assertEqual(response.status_int, 404)
        response = self.app.get(reverse('tourism:companion:read', args=(companion_f_u.pk,)),
                                expect_errors=True)
        self.assertEqual(response.status_int, 404)

        response = self.app.get(reverse('tourism:companion:read', args=(companion_t_e.pk,)),
                                user=self.user)
        self.assertEqual(response.context['companion'], companion_t_e)
        response = self.app.get(reverse('tourism:companion:read', args=(companion_t_u.pk,)),
                                user=self.user)
        self.assertEqual(response.context['companion'], companion_t_u)
        response = self.app.get(reverse('tourism:companion:read', args=(companion_f_e.pk,)),
                                user=self.user, expect_errors=True)
        self.assertEqual(response.status_int, 404)
        response = self.app.get(reverse('tourism:companion:read', args=(companion_f_u.pk,)),
                                user=self.user)
        self.assertEqual(response.context['companion'], companion_f_u)

    def test_my_companion(self):
        """Собственные объявления пользователя"""

        companion_t_u = G(Companion, n=3, visible=True, author=self.user)
        companion_f_u = G(Companion, n=4, visible=False, author=self.user)
        companion_t_e = G(Companion, n=5, visible=True, author=self.evil_user)
        companion_f_e = G(Companion, n=6, visible=False, author=self.evil_user)

        response = self.app.get(reverse('tourism:companion:my'), expect_errors=True)
        self.assertEqual(response.status_int, 302)

        response = self.app.get(reverse('tourism:companion:my'), user=self.user)
        self.assertTemplateUsed(response, 'tourism/companion/my.html')
        self.assertEqual(len(response.context['companions']), len(companion_t_u))

        response = self.app.get(reverse('tourism:companion:my'), user=self.evil_user)
        self.assertEqual(len(response.context['companions']), len(companion_t_e))

        response = self.app.get(u'%s?visible=0' % reverse('tourism:companion:my'), user=self.user)
        self.assertEqual(len(response.context['companions']), len(companion_f_u))

        response = self.app.get(u'%s?visible=0' % reverse('tourism:companion:my'), user=self.evil_user)
        self.assertEqual(len(response.context['companions']), len(companion_f_e))

    def test_index(self):
        """Главная компаньона (страница поиска)"""

        G(Companion, n=5)
        response = self.app.get(reverse('tourism:companion:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/companion/search.html')
        self.assertEqual(len(response.context['companions']), 5)

    def test_create(self):
        """Добавление"""

        params = {
            'my_composition': 2,
            'find_composition': 2,
            'place': self.random_string(250),
            'description': self.random_string(2000),
            'name': self.random_string(250),
            'about': self.random_string(250),
            'phone': self.random_string(250),
            'email': 'example@example.com',
            'visible': True,
        }

        self.app.post(reverse('tourism:companion:create'), params=urlencode(params), user=self.user)
        companion = Companion.objects.all()[0]
        self.assertTrue(companion)
        self.assertEquals(companion.my_composition, params['my_composition'])
        self.assertEquals(companion.find_composition, params['find_composition'])
        self.assertEquals(companion.place, params['place'])
        self.assertEquals(companion.description, params['description'])
        self.assertEquals(companion.name, params['name'])
        self.assertEquals(companion.about, params['about'])
        self.assertEquals(companion.phone, params['phone'])
        self.assertEquals(companion.email, params['email'])
        self.assertEquals(companion.visible, params['visible'])

    def test_update(self):
        """Редактирование"""

        companion = G(Companion, author=self.user)
        params = {
            'my_composition': 3,
            'find_composition': 3,
            'place': self.random_string(250),
            'description': self.random_string(2000),
            'name': self.random_string(250),
            'about': self.random_string(250),
            'phone': self.random_string(250),
            'email': 'example2@example.com',
            'visible': False,
        }

        self.app.post(reverse('tourism:companion:edit', args=(companion.pk,)),
                      params=urlencode(params), user=self.user)
        companion = Companion.objects.all()[0]
        self.assertTrue(companion)
        self.assertEquals(companion.my_composition, params['my_composition'])
        self.assertEquals(companion.find_composition, params['find_composition'])
        self.assertEquals(companion.place, params['place'])
        self.assertEquals(companion.description, params['description'])
        self.assertEquals(companion.name, params['name'])
        self.assertEquals(companion.about, params['about'])
        self.assertEquals(companion.phone, params['phone'])
        self.assertEquals(companion.email, params['email'])
        self.assertEquals(companion.visible, params['visible'])

    def test_delete(self):
        """Удаление"""

        companion = G(Companion, author=self.user)
        self.app.get(reverse('tourism:companion:delete', args=(companion.pk,)), user=self.user)
        companions = Companion.objects.filter(pk=companion.pk)
        self.assertFalse(companions)
