# -*- coding: utf-8 -*-

from irk.utils.http import ajax_request

from irk.push_notifications.models import Device, Message
from irk.push_notifications.tasks import send_message_for_device_task


@ajax_request
def subscribe(request):
    """Создать подписку на push уведомления"""

    endpoint = request.json.get('endpoint')
    if not endpoint:
        return {'ok': False, 'msg': 'Endpoint required'}

    user = request.user
    if user.is_anonymous:
        user = None

    device, created = Device.objects.update_or_create(registration_id=endpoint, driver=Device.DRIVER_FCM, defaults={
        'is_active': True, 'user': user
    })

    if created:
        message = Message.objects.filter(alias='welcome').first()
        if message:
            send_message_for_device_task.delay(device.id, message.id)

    return {'ok': True, 'msg': 'Subscribe successfully'}


@ajax_request
def unsubscribe(request):
    """Отменить подписку на push уведомлений"""

    endpoint = request.json.get('endpoint')
    if not endpoint:
        return {'ok': False, 'msg': 'Endpoint required'}

    device = Device.objects.filter(registration_id=endpoint).first()
    if not device:
        return {'ok': False, 'msg': 'Device not found'}

    device.is_active = False
    device.save()

    return {'ok': True, 'msg': 'Subscription canceled '}
