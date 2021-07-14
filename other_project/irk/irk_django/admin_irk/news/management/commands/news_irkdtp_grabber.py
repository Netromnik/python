# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from irk.news.helpers.grabbers import FlashFromVkGrabber


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = u'Грабер народных новостей из группы irkdtp Вконтакта'

    def handle(self, **options):
        logger.debug('Start grab from vk.com/irkdtp')

        grab = FlashFromVkGrabber()
        grab.run()

        logger.debug('Finish grab from vk.com/irkdtp')
