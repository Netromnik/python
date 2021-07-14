# -*- coding: utf-8 -*-

"""Модуль содержит классы и функции для отправки push-уведомлений на конкретные виды устройств и браузеров"""

import logging
import threading
from abc import ABCMeta, abstractmethod
from Queue import Queue

import requests
from pyfcm import FCMNotification

from django.conf import settings

from irk.push_notifications.models import Device, Distribution
from irk.utils.exceptions import raven_capture

logger = logging.getLogger(__name__)


class DriverError(Exception):
    pass


class Driver(object):
    """Базовый класс драйвера"""

    __metaclass__ = ABCMeta

    def send(self, devices, message):
        """Отправка сообщения на множество девайсов"""

        # изменить статус доставки
        Distribution.objects.filter(device__in=devices, message=message).delete()
        Distribution.objects.bulk_create((
                Distribution(device=device, message=message, status=Distribution.STATUS_SENT)
                for device in devices
            ), batch_size=1000
        )
        # получить reg_ids
        reg_ids = [device.get_reg_id() for device in devices]
        # отправить месседж
        try:
            invalid_regs = self.send_notification(reg_ids)
            self.delete(invalid_regs)
        except Exception as err:
            raven_capture(err)
            logger.exception(err)
        # установить время отправки
        message.set_sent_date()

    @abstractmethod
    def send_notification(self, reg_ids):
        """
        Отправка push уведомления на устройство.

        Тело сообщения получается через ajax-запрос после того, как девайс получит и обработате push уведомление

        :return: список недействительных девайсов
        :rtype: set
        """

        return set()

    def delete(self, invalid_regs):
        """
        Удаление недействительных девайсов

        :param set invalid_regs: список недействительных идентификаторов девайсов
        """

        count = Device.objects.filter(registration_id__in=invalid_regs).count()
        Device.objects.filter(registration_id__in=invalid_regs).delete()
        logger.info(u'Remove {} invalid devices'.format(count))


class FCMDriver(Driver):
    """
    Драйвер для Firebase Cloud Messaging
    """

    def __init__(self, *args, **kwargs):
        super(FCMDriver, self).__init__(*args, **kwargs)

        self._api = FCMNotification(api_key=settings.PUSH_NOTIFICATIONS_SETTINGS['FCM_API_KEY'])
        self._invalid_regs = set()

    def send_notification(self, reg_ids):
        # Разбиваем все идентификаторы на порции по 1000 в каждой
        chunks = (reg_ids[i:i+1000] for i in range(0, len(reg_ids), 1000))

        for chunk in chunks:
            info = self._api.notify_multiple_devices(registration_ids=chunk)
            self._pull_invalid_regs(info)

        self._normalize_invalid_regs()

        return self._invalid_regs

    def _pull_invalid_regs(self, info):
        """Вытянуть информацию о недействительных девайсах из данных от FCM"""

        if 'errors' in info:
            self._invalid_regs.update(info['errors'].get('InvalidRegistration', []))
            self._invalid_regs.update(info['errors'].get('NotRegistered', []))

    def _normalize_invalid_regs(self):
        """
        Приводит недействительные registration id к нормальной форме

        FCM возращает registration id в сокращенной форме.
        Для удаления нужно их привести к форме в которой они хранятся в БД.
        """

        prefix = 'https://fcm.googleapis.com/fcm/send/'

        self._invalid_regs = {prefix + reg_id for reg_id in self._invalid_regs}


# TODO Больше не используется
class MozillaDriver(Driver):
    """Драйвер для Firefox'a"""

    def send_notification(self, reg_ids):
        invalid_regs = set()
        for reg_id in reg_ids:
            try:
                response = requests.post(reg_id, timeout=10)
                if response.status_code in (404, 410):
                    invalid_regs.add(reg_id)
                    continue
                response.raise_for_status()
            except requests.RequestException as err:
                raven_capture(err)
                continue

        return invalid_regs


# TODO Больше не используется
class ConcurrentMozillaDriver(Driver):
    """Многопоточный драйвер для Firefox'a"""

    concurrency = 100
    timeout = 10

    def __init__(self, *args, **kwargs):
        super(ConcurrentMozillaDriver, self).__init__(*args, **kwargs)

        self._queue = Queue(self.concurrency * 2)
        self._invalid_regs = set()
        self._lock = threading.Lock()

    def send_notification(self, reg_ids):
        logger.debug(u'Start send notifications for firefox users')

        self._run_handlers()
        for reg_id in reg_ids:
            self._queue.put(reg_id)

        self._queue.join()
        logger.debug(u'Finish send notifications for firefox users')

        return self._invalid_regs

    def _handle(self):
        """Обработчик. Посылает POST запрос на определенный url"""

        while True:
            url = self._queue.get()
            try:
                response = requests.post(url, timeout=self.timeout, headers=self.get_headers())
                # endpoint not valid
                if response.status_code in (404, 410):
                    with self._lock:
                        self._invalid_regs.add(url)
                    continue
                response.raise_for_status()
                logger.debug(u'Success send notification for {}'.format(url))
            except requests.RequestException as err:
                raven_capture(err)
                message = u'Fail send notification. Error: {}'.format(err)
                if err.response:
                    message += u' code: {code}, errno: {errno}. {message}'.format(err.response.json())
                logger.error(message)
                continue
            finally:
                self._queue.task_done()

    def _run_handlers(self):
        """Стартует пул обработчиков"""

        for i in range(self.concurrency):
            t = threading.Thread(target=self._handle)
            t.daemon = True
            t.start()

        logger.debug(u'Run {} handlers'.format(self.concurrency))

    def get_headers(self):
        """Получить словарь необходимых заголовков для запроса"""

        return {
            # Время жизни уведомления обязательный параметр
            # подробнее: https://webpush-wg.github.io/webpush-protocol/#rfc.section.5.2
            'TTL': '86400',    # сообщение действительно одни сутки
        }


def get_driver(_):
    """
    Получить драйвер по ключу.

    После перехода на FCM отдельный драйвер для мозиллы стал не нужен
    """

    return FCMDriver()
