# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.core.management.base import BaseCommand, CommandError

from irk.afisha.tickets.binder import TicketBinder, get_ticket_event
from irk.afisha.tickets.creator import get_ticket_creator
from irk.afisha.tickets.kassy import KassyGrabber
from irk.afisha.tickets.kinomax import KinomaxGrabber
from irk.afisha.tickets.rambler import RamblerGrabber

log = logging.getLogger(__name__)

grabbers = {
    'rambler': RamblerGrabber,
    'kassy': KassyGrabber,
    'kinomax': KinomaxGrabber,
}


class Command(BaseCommand):
    help = u'Команда для работы с билетными системами в Афише'

    def add_arguments(self, parser):
        parser.add_argument('label', help='Метка билетной системы', choices=['kassy', 'rambler', 'kinomax'])

        parser.add_argument('cmd', help='Команда', choices=['grab', 'bind', 'create'])

        parser.add_argument('event', help='Идентификатор события в билетной системе', nargs='?', default='all')

    def handle(self, **options):
        if options['cmd'] == 'grab':
            grabber = grabbers.get(options['label'])()
            if not grabber:
                raise CommandError('Not found {} grabber'.format(options['label']))
            grabber.run()
        elif options['cmd'] == 'bind':
            binder = TicketBinder(options['label'])
            binder.update_all_events()
        elif options['cmd'] == 'create':
            if options['label'] == 'kassy':
                raise CommandError('Kassy do not support the creation of sessions')

            creator = get_ticket_creator(options['label'])
            if options['event'] == 'all':
                creator.create_for_all_events()
            else:
                ticket_event = get_ticket_event(options['label'], options['event'])
                creator.create(ticket_event)
