# -*- coding: utf-8 -*-

from django_dynamic_fixture import G

from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase

from irk.push_notifications.models import Device, Message, Distribution


class SubscribeTest(UnitTestBase):
    """Подписка устройства"""

    csrf_checks = False

    def setUp(self):
        self.url = reverse('push_notifications:subscribe')

    def test_default(self):
        """Стандартная работа"""

        endpoint = 'https://android.googleapis.com/gcm/send/ctUxG1zwaB0:APA91bFreFoRCTxixsi...'
        data = {
            'endpoint': endpoint
        }

        response = self.ajax_post(self.url, data)

        self.assertTrue(response.json['ok'])
        self.assertTrue(Device.objects.filter(registration_id=endpoint).exists())

    def test_not_endpoint(self):
        """Не указан endpoint устройства"""

        data = {
            'param': 'value'
        }

        response = self.ajax_post(self.url, data)

        self.assertFalse(response.json['ok'])

    def test_not_supported_device(self):
        """Неподдерживаемый тип устройства"""

        data = {
            'endpoint': 'https://vendor_not_support/adc:qwertyuiop'
        }

        response = self.ajax_post(self.url, data)

        self.assertFalse(response.json['ok'])

    def test_anonymous_user(self):
        """Анонимный пользователь"""

        endpoint = 'https://android.googleapis.com/gcm/send/ctUxG1zwaB0:APA91bFreFoRCTxixsi...'
        data = {
            'endpoint': endpoint
        }

        self.ajax_post(self.url, data)

        device = Device.objects.get(registration_id=endpoint)
        self.assertIsNone(device.user)

    def test_registered_user(self):
        """Зарегистрированный пользователь"""

        endpoint = 'https://android.googleapis.com/gcm/send/ctUxG1zwaB0:APA91bFreFoRCTxixsi...'
        data = {
            'endpoint': endpoint
        }
        user = self.create_user('user', 'password')

        self.ajax_post(self.url, data, user=user)

        device = Device.objects.get(registration_id=endpoint)
        self.assertEqual(user, device.user)

    def test_double_subscribe(self):
        """Обработка случая повторных подписок"""

        endpoint = 'https://android.googleapis.com/gcm/send/ctUxG1zwaB0:APA91bFreFoRCTxixsi...'
        data = {
            'endpoint': endpoint
        }

        self.ajax_post(self.url, data)
        self.assertEqual(1, Device.objects.filter(registration_id=endpoint).count())

        # Повторно отправляем теже данные
        self.ajax_post(self.url, data)
        self.assertEqual(1, Device.objects.filter(registration_id=endpoint).count())


class UnsubscribeTest(UnitTestBase):
    """Отписка устройства"""

    csrf_checks = False

    def setUp(self):
        self.url = reverse('push_notifications:unsubscribe')
        self.endpoint = 'https://android.googleapis.com/gcm/send/ctUxG1zwaB0:APA91bFreFoRCTxixsi...'
        self.device = G(Device, registration_id=self.endpoint, is_active=True, user=None)

    def test_default(self):
        """Стандартная работа"""

        data = {
            'endpoint': self.endpoint,
        }

        response = self.ajax_post(self.url, data)
        self.assertTrue(response.json['ok'])
        self.assertFalse(Device.objects.get(registration_id=self.endpoint).is_active)

    def test_not_endpoint(self):
        """Нет параметра endpoint"""

        data = {
            'other': self.endpoint,
        }

        response = self.ajax_post(self.url, data)
        self.assertFalse(response.json['ok'])

    def test_device_does_not_exist(self):
        """Нет девайса с таким endpoint'ом"""

        data = {
            'endpoint': 'other endpoint',
        }

        response = self.ajax_post(self.url, data)
        self.assertFalse(response.json['ok'])
