# -*- coding: utf-8 -*-

"""Задачи celery"""

from irk.utils.tasks.helpers import make_command_task

# В течение двух часов каждые пять минут пытаемся перезапустить задачу
currency_grabber_exchange = make_command_task('currency_grabber_exchange', retry=True, countdown=60 * 5, max_retries=24)

