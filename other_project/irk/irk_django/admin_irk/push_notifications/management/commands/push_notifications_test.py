# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.core.management.base import BaseCommand

from irk.push_notifications.models import Device, Message
from irk.push_notifications.controllers import PushController


logger = logging.getLogger(__name__)


def send_message_for_device_task(device_id, message_id):
    """Задача на отправку сообщения"""

    device = Device.objects.filter(id=device_id).first()
    if not device:
        logger.error('Not found device with id: {}'.format(device_id))
        return

    message = Message.objects.filter(id=message_id).first()
    if not message:
        logger.error('Not found message with id: {}'.format(message_id))
        return

    ctrl = PushController()
    ctrl.send_for_device(device, message)


class Command(BaseCommand):
    help = 'Очистить список зарегистрированных устройств. Удаляются неативные'

    def add_arguments(self, parser):
        parser.add_argument('-device', nargs='+', type=str)

    def handle(self, **options):
        device = Device.objects.filter(registration_id=options['device'][0]).order_by('-created').first()
        message = Message.objects.all().first()
        send_message_for_device_task(device.pk, message.pk)
