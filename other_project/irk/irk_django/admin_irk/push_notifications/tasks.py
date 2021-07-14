# -*- coding: utf-8 -*-

import logging

from irk.push_notifications.controllers import PushController
from irk.push_notifications.models import Device, Message
from irk.utils.tasks.helpers import make_command_task, task

logger = logging.getLogger(__name__)


push_notifications_clean_devices = make_command_task('push_notifications_clean_devices')


@task(ignore_result=True, max_retries=3, default_retry_delay=5)
def send_message_for_all_task(message_id):
    """Задача на отправку сообщения"""

    message = Message.objects.filter(id=message_id).first()
    if not message:
        logger.error('Not found message with id: {}'.format(message_id))
        return

    ctrl = PushController()
    ctrl.send_for_all(message)


@task(ignore_result=True, max_retries=3, default_retry_delay=5)
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
