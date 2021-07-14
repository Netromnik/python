# -*- coding: utf-8 -*-

import os.path
import datetime

from django.conf import settings
from django.db import models

from irk.push_notifications.managers import DeviceManager


class Device(models.Model):
    """Устройство или браузер на которое отправляется push notification"""

    DRIVER_FCM = 1
    DRIVER_MOZILLA = 2
    DRIVER_CHOICES = (
        (DRIVER_FCM, 'google'),
        (DRIVER_MOZILLA, 'firefox'),
    )

    registration_id = models.CharField(u'идентификатор', max_length=300)
    driver = models.PositiveSmallIntegerField(u'транспорт', choices=DRIVER_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=u'пользователь')
    is_active = models.BooleanField(u'активен', default=True, db_index=True)

    created = models.DateTimeField(u'создан', auto_now_add=True, editable=False)
    modified = models.DateTimeField(u'модифицирован', auto_now=True, editable=False)

    objects = DeviceManager

    class Meta:
        verbose_name = u'устройство'
        verbose_name_plural = u'устройства'

    def __unicode__(self):
        return u'User: {0.user} Driver: {1} Active: {0.is_active}'.format(self, self.get_driver_display())

    def get_reg_id(self):
        """Получить идентификатор для отправки сообщений"""

        # Для драйвера FCM необходимо взять последний элемент пути в registration_id
        if self.driver == self.DRIVER_FCM:
            return self.registration_id.replace('https://fcm.googleapis.com/fcm/send', '').strip('/')

        return self.registration_id


class Message(models.Model):
    """Сообщение"""

    title = models.CharField(u'заголовок', max_length=255)
    text = models.TextField(u'текст')
    link = models.URLField(u'ссылка', blank=True)
    alias = models.CharField(u'алиас', max_length=50, blank=True, db_index=True)
    devices = models.ManyToManyField(
        'push_notifications.Device', through='push_notifications.Distribution', related_name='messages'
    )

    created = models.DateTimeField(u'создано', auto_now_add=True, editable=False)
    sent = models.DateTimeField(u'отправлено', null=True, editable=False)

    class Meta:
        verbose_name = u'сообщение'
        verbose_name_plural = u'сообщения'

    def __unicode__(self):
        return self.title

    def set_sent_date(self, stamp=None):
        """Установить время отправки"""

        stamp = stamp or datetime.datetime.now()

        self.sent = stamp
        self.save()


class Distribution(models.Model):
    """Рассылка сообщений"""

    STATUS_SENT = 1
    STATUS_RECEIVED = 2
    STATUS_CHOICES = (
        (STATUS_SENT, u'отправлено'),
        (STATUS_RECEIVED, u'получено'),
    )

    device = models.ForeignKey('push_notifications.Device', verbose_name=u'устройство подписчика')
    message = models.ForeignKey('push_notifications.Message', verbose_name=u'сообщение')
    status = models.PositiveSmallIntegerField(u'статус', choices=STATUS_CHOICES, default=STATUS_SENT, db_index=True)

    created = models.DateTimeField(u'создана', auto_now_add=True, editable=False)
    modified = models.DateTimeField(u'модифицирована', auto_now=True, editable=False)

    class Meta:
        verbose_name = u'рассылка'
        verbose_name_plural = u'рассылки'
        unique_together = ('device', 'message')

    def set_status_received(self):
        """Установить статус рассылки в «получено»"""

        self.status = self.STATUS_RECEIVED
        self.save()

