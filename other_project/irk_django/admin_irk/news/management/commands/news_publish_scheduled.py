# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import logging

from django.core.management.base import BaseCommand
from irk.news.models import ScheduledTask, BaseMaterial


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Опубликовать запланированные материалы"""

    help = 'Опубликовать материалы, время публикации которых пришло'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        logger.debug('Starting news_publish_scheduled command at %s', now)

        tasks = ScheduledTask.get_due_tasks(now)
        for task in tasks:
            logger.debug(' Task id=%s when=%s material=%s', task.id, task.when, task.material.title)
            task.run()

        logger.debug('Finished')

