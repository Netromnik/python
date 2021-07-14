# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from irk.afisha import models as m
from irk.afisha.tickets.kassy import KassyGrabber


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = u'''\
    Обновить данные по кассам.ру

    Старые данные будут удалены! Все привязки нужно делать заново.
    '''

    def handle(self, **options):
        logger.debug('Start refresh kassy')

        m.KassySession.objects.all().delete()
        m.KassyEvent.objects.all().delete()
        m.KassyRollerman.objects.all().delete()
        m.KassyHall.objects.all().delete()
        m.KassyBuilding.objects.all().delete()

        grab = KassyGrabber()
        grab.run()

        logger.debug('Finish refresh kassy')
