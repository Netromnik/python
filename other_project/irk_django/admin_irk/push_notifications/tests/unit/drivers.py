# -*- coding: utf-8 -*-

import mock
from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase

from irk.push_notifications.models import Device, Message, Distribution


class GCMDriverTest(UnitTestBase):
    """Тесты драйвера GCM"""

    def setUp(self):
        gcm_patcher = mock.patch('push_notifications.drivers.GCM')
        self.gcm = gcm_patcher.start()
        self.addCleanup(gcm_patcher.stop)

        from push_notifications.drivers import FCMDriver
        self.driver = FCMDriver()

    def test_send_single(self):
        """Отправка сообщения на одно устройство"""

        device = G(Device, driver=Device.DRIVER_GCM, is_active=True, user=None)

        message = G(Message)
        self.driver.send([device], message)

        distribution = Distribution.objects.filter(device=device, message=message).first()
        self.assertIsNotNone(distribution)
        self.assertEqual(distribution.status, Distribution.STATUS_SENT)
        self.assertIsNotNone(Message.objects.get(id=message.id).sent)

    def test_send_multi(self):
        """Отправка сообщения на несколько устройств"""

        devices = G(Device, driver=Device.DRIVER_GCM, is_active=True, user=None, n=15)

        message = G(Message)
        self.driver.send(devices, message)

        self.assertIsNotNone(Message.objects.get(id=message.id).sent)

        for device in devices:
            distribution = Distribution.objects.filter(device=device, message=message).first()
            self.assertIsNotNone(distribution)
            self.assertEqual(distribution.status, Distribution.STATUS_SENT)


class MozillaDriverTest(UnitTestBase):
    """Тесты драйвера GCM"""

    def setUp(self):
        requests_patcher = mock.patch('push_notifications.drivers.requests')
        self.requests = requests_patcher.start()
        self.addCleanup(requests_patcher.stop)

        from push_notifications.drivers import ConcurrentMozillaDriver
        self.driver = ConcurrentMozillaDriver()

    def test_send_single(self):
        """Отправка сообщения на одно устройство"""

        device = G(Device, driver=Device.DRIVER_MOZILLA, is_active=True, user=None)

        message = G(Message)
        self.driver.send([device], message)

        distribution = Distribution.objects.filter(device=device, message=message).first()
        self.assertIsNotNone(distribution)
        self.assertEqual(distribution.status, Distribution.STATUS_SENT)
        self.assertIsNotNone(Message.objects.get(id=message.id).sent)

    def test_send_multi(self):
        """Отправка сообщения на несколько устройств"""

        devices = G(Device, driver=Device.DRIVER_MOZILLA, is_active=True, user=None, n=15)

        message = G(Message)
        self.driver.send(devices, message)

        self.assertIsNotNone(Message.objects.get(id=message.id).sent)

        for device in devices:
            distribution = Distribution.objects.filter(device=device, message=message).first()
            self.assertIsNotNone(distribution)
            self.assertEqual(distribution.status, Distribution.STATUS_SENT)
