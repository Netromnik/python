# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from irk.news.models import DailyNewsletter
from irk.news.helpers import NewsletterController

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = u'Разослать ежедневную рассылку новостей и материалов'

    def handle(self, **options):
        logger.debug('Start send daily distribution')

        newsletter = DailyNewsletter.get_current()
        controller = NewsletterController(newsletter)
        controller.distribute()

        logger.debug('Finish send daily distribution')
