# -*- coding: utf-8 -*-

"""Задачи celery"""

import logging
import redis

from django.conf import settings

from irk.utils.tasks.helpers import make_command_task, task
from irk.utils.grabber import proxy_requests

from irk.tourism import settings as app_settings


logger = logging.getLogger(__name__)


tourism_hide_old_tours = make_command_task('tourism_hide_old_tours')


@task
def check_360baikalru_availability():
    """Проверка работоспособности сайта 360baikal.ru

    Если сайт не работает, в местах отдыха Туризма должны скрываться панорамы
    """

    connection = redis.StrictRedis(host=settings.REDIS['default']['HOST'], db=settings.REDIS['default']['DB'])

    try:
        response = proxy_requests.head('http://360baikal.ru')
        response.raise_for_status()
    except proxy_requests.HTTPError:
        # Задача запускается раз в 5 минут, ключ живет чуть дольше
        connection.setex(app_settings.BAIKAL360_AVAILABILITY_KEY, 60 * 6, '0')
        logger.warning('360baikal.ru domain is unavailable. Hiding panoramas now!')
    else:
        connection.delete(app_settings.BAIKAL360_AVAILABILITY_KEY)
        logger.debug('360baikal.ru domain is alive. Everything is ok!')
