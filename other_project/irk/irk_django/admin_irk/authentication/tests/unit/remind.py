# -*- coding: utf-8 -*-

from __future__ import absolute_import

import json
import unittest

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.profiles.models import Profile
from irk.sms.models import PhoneNumber
from irk.tests.unit_base import UnitTestBase
from irk.utils.db.kv import get_redis


@unittest.skip(u"Не тестируем восстановление пароля")
class RemindTestCase(UnitTestBase):
    """Тесты на восстановление пароля"""

    csrf_checks = False

    def setUp(self):
        super(RemindTestCase, self).setUp()
        G(PhoneNumber, range_min=9500000000, range_max=9509999999)
        self.password = '123'
        self.phone = '9501234567'
        self.email = 'user@example.com'

    @staticmethod
    def mock_receive_code(phone):
        redis = get_redis()
        return redis.get('auth.join.phone_confirm.{0}'.format(phone))

    def test_index_phone(self):
        """Востановление пароля через телефон"""

        user = self.create_user('user', password=self.password)
        profile = Profile.objects.get(user=user)
        profile.phone = self.phone
        profile.save()

        url = reverse('authentication:remind')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/remind.html')

        response = self.app.post(url, params={'phone_email': self.phone, },
                                 headers={'X_REQUESTED_WITH': 'XMLHttpRequest', })
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertEqual(json_data['success'], True)
        self.assertEqual(json_data['is_phone'], True)

        code = self.mock_receive_code(self.phone)
        url = reverse('authentication.remind.phone.confirm')
        response = self.app.post(url, params={'code': code, }, headers={'X_REQUESTED_WITH': 'XMLHttpRequest', })
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertEqual(json_data['success'], True)

    def test_index_email(self):
        """Востановление пароля через email"""

        user = self.create_user('user', password=self.password)
        profile = Profile.objects.get(user=user)
        profile.hash_stamp = None
        profile.save()

        url = reverse('authentication:remind')
        response = self.app.post(url, params={'phone_email': self.email, },
                                 headers={'X_REQUESTED_WITH': 'XMLHttpRequest', })
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertEqual(json_data['success'], True)
        self.assertEqual(json_data['is_phone'], False)

        profile = Profile.objects.get(user=user)
        self.assertTrue(profile.hash)
        self.assertTrue(profile.hash_stamp)

    def test_remind_without_ajax_phone(self):
        """Восстановление без ajax через телефон"""

        user = self.create_user('user', password=self.password)
        profile = Profile.objects.get(user=user)
        profile.phone = self.phone
        profile.save()

        url = reverse('authentication:remind')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/remind.html')

        response = self.app.post(url, params={'phone_email': self.phone, }).follow()
        self.assertEqual(response.status_code, 200)

        code = self.mock_receive_code(self.phone)
        url = reverse('authentication.remind.phone.confirm')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/users/phone/confirm.html')

        response = self.app.post(url, params={'code': code, }).follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/users/update_password.html')

    def test_remind_without_ajax_email(self):
        """Восстановление без ajax через email"""

        user = self.create_user('user', password=self.password)
        profile = Profile.objects.get(user=user)
        profile.hash_stamp = None
        profile.save()

        url = reverse('authentication:remind')
        response = self.app.post(url, params={'phone_email': self.email, })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/remind_ok.html')
