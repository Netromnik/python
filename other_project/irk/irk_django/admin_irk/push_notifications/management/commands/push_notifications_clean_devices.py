# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import logging

from django.core.management.base import BaseCommand

from irk.push_notifications.models import Device


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Очистить список зарегистрированных устройств. Удаляются неативные'

    def handle(self, **options):
        logger.debug('Start clean devices')

        stamp = datetime.date.today() - datetime.timedelta(days=30)
        qs = Device.objects.filter(is_active=False, modified__lte=stamp)
        count = qs.count()
        qs.delete()
        logger.info('Deleted {} devices'.format(count))
        logger.debug('Finish clean devices')
