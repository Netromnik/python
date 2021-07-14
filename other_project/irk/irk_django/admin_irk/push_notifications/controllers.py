# -*- coding: utf-8 -*-

import logging

from irk.push_notifications.drivers import get_driver, DriverError
from irk.push_notifications.models import Device
from irk.utils.metrics import newrelic_record_timing


log = logging.getLogger(__name__)


class PushController(object):
    """Контроллер для отправки push notifications"""

    @newrelic_record_timing('Custom/Push/ForAll')
    def send_for_all(self, message):
        """Отправить сообщение на все активные устройства"""

        for driver_type, driver_name in Device.DRIVER_CHOICES:
            try:
                driver = get_driver(driver_type)
                devices = Device.objects.filter(driver=driver_type, user_id=54402).active()
                driver.send(devices, message)
            except DriverError as err:
                log.error('Fail send message by driver {}. Error: {}'.format(driver_name, err))
                continue

    @newrelic_record_timing('Custom/Push/ForDevice')
    def send_for_device(self, device, message):
        """Отправить сообщение на устройство"""

        try:
            driver = get_driver(device.driver)
            driver.send([device], message)
        except DriverError as err:
            log.error('Fail send message by driver {}. Error: {}'.format(device.get_driver_display(), err))
