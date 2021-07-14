# -*- coding: utf-8 -*-

import logging
import datetime
import random

from django.core.files.base import ContentFile

try:
    from django.contrib.auth.models import get_hexdigest
except ImportError:
    from irk.authentication.helpers import get_hexdigest
from irk.news.models import Subscriber
from irk.authentication.helpers import generate_identicon


logger = logging.getLogger(__name__)


def set_subscriber(sender, instance, **kwargs):
    """
    Создается рассылка для пользователя подписавшегося пользователя и удаляется для отписавшегося
    """

    if not instance.subscribe:
        Subscriber.objects.filter(user=instance.user).delete()
    else:
        try:
            Subscriber.objects.filter(user=instance.user)[0]
        except IndexError:

            hash_ = get_hexdigest('sha1', str(random.random()), str(random.random()))

            subscriber = Subscriber(email=instance.user.email, user=instance.user, hash_stamp=datetime.datetime.now(),
                                    hash=hash_)
            subscriber.save()


def create_blank_avatar(sender, instance, created, **kwargs):
    """Генерация аватарки по умолчанию для пользователя"""

    if instance.image:
        return

    content = generate_identicon(instance.user_id)
    instance.image.save('identicon.png', ContentFile(content.getvalue()))

    logger.debug('Created identicon for user #{0}'.format(instance.user_id))
