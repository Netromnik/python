# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import logging

from django.core.management.base import BaseCommand
from irk.scheduler.tasks import SocpultScheduler


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Опубликовать запланированные посты в соцсети"""

    help = 'Опубликовать посты в соцсети, время публикации которых пришло'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        logger.debug('Starting scheduler_socpult command at %s', now)

        scheduler = SocpultScheduler()
        scheduler.tick()

        logger.debug('Finished')

