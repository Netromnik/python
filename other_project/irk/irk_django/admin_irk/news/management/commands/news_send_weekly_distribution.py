# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from irk.news.models import WeeklyNewsletter
from irk.news.helpers import NewsletterController

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = u'Разослать еженедельную рассылку новостей и материалов'

    def handle(self, **options):
        logger.debug('Start send weekly distribution')

        newsletter = WeeklyNewsletter.get_current()
        controller = NewsletterController(newsletter)
        controller.distribute()

        logger.debug('Finish send weekly distribution')
