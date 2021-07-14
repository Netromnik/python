# -*- coding: utf-8 -*-

from __future__ import absolute_import
import json

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.profiles.models import Profile
from irk.sms.models import PhoneNumber
from irk.tests.unit_base import UnitTestBase
from irk.utils.db.kv import get_redis


class RegisterTestCase(UnitTestBase):
    """Тесты регистрации"""

    csrf_checks = False

    def setUp(self):
        super(RegisterTestCase, self).setUp()
        G(PhoneNumber, range_min=9500000000, range_max=9509999999)
        self.password = '123'
        self.phone = '9501234567'
        self.email = 'user@example.com'
        self.name = self.random_string(6)

    @staticmethod
    def mock_receive_code(phone):
        redis = get_redis()
        return redis.get('auth.join.phone_confirm.{0}'.format(phone))

    def test_check_phone(self):
        """Проверка номера телефона на валидность"""

        url = reverse('authentication.views.register.check_phone')
        response = self.app.get(url, params={'number': self.phone})
        self.assertEqual(response.status_code, 200)
        data = json.loads(unicode(response.content))
        self.assertEqual(data['number'], self.phone)

        # Левый телефон
        response = self.app.get(url, params={'number': '9241234567'}, status='*')
        self.assertEqual(response.status_code, 404)

        # Занятый уже телефон
        G(Profile, phone=self.phone)
        response = self.app.get(url, params={'number': self.phone})
        data = json.loads(response.content)
        self.assertTrue(data['error'])

    def test_register_phone(self):
        """Регистрация через телефон"""

        url = reverse('authentication.views.register.phone')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register/phone.html')

        response = self.app.post(url, params={'phone': self.phone, }).follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register/details.html')

        response = self.app.post(reverse('authentication.views.register.details'), params={
            'code': self.mock_receive_code(self.phone),
            'name': self.name,
            'password': self.password}
        ).follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register/success.html')
        self.assertTrue(Profile.objects.filter(full_name=self.name).exists())
