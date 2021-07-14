# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import logging

from django.db.models.signals import post_save

from irk.afisha import models as m
from irk.afisha.sessions import update_cache_table

log = logging.getLogger(__name__)


def get_ticket_creator(label):
    """Return ticket creator class by label"""

    from irk.afisha.tickets.rambler import RamblerTicketCreator
    from irk.afisha.tickets.kinomax import KinomaxTicketCreator

    label_to_creator = {
        'rambler': RamblerTicketCreator,
        'kinomax': KinomaxTicketCreator,
    }

    return label_to_creator.get(label)()


class TicketCreator(object):
    """
    Create all needed models for binding ticket events

    Create EventGuide, Period, Sessions
    """

    HALL_MODEL = None
    EVENT_MODEL = None
    SOURCE = None

    def parse_periods(self):
        """Return periods for ticket sessions"""

        raise NotImplementedError

    def create_period(self, event_guide, period_info):
        """Create single period"""

        raise NotImplementedError

    def create_sessions(self, period, period_info):
        """Create sessions for period by times"""

        raise NotImplementedError

    def _initialize(self, ticket_event):
        self._ticket_event = ticket_event
        self._event = ticket_event.event
        self._ticket_sessions = ticket_event.sessions.filter(is_ignore=False)

    def create(self, ticket_event):
        """Create EventGuides, Periods, Sessions for event binding with ticket_event"""
        self._initialize(ticket_event)
        log.debug(
            'Start creating sessions for {} event: {}'.format(self._event, ticket_event.ticket_label)
        )
        self.disable_signals()
        self.remove_event_guides()
        self.create_periods()
        self.enable_signals()
        log.debug(
            'Finish creating sessions for event {} from {}'.format(self._event, ticket_event.ticket_label)
        )

    def create_for_all_events(self):
        """Create sessions for all ticket events are binding with events"""

        log.debug('Start creating sessions for all events')

        stamp = datetime.datetime.now() - datetime.timedelta(days=60)
        ticket_events = self.EVENT_MODEL.objects.filter(event__isnull=False, date_start__gte=stamp)
        self.disable_signals()

        for ticket_event in ticket_events:
            self._initialize(ticket_event)
            self.remove_event_guides()
            self.create_periods()
            log.debug('Created sessions for {} from {}'.format(self._event, ticket_event.ticket_label))

        self.enable_signals()

        log.debug('Finish creating sessions for all events')

    def create_periods(self):
        """Create all periods"""

        event_guides = self.create_event_guides()
        for period_info in self.parse_periods():
            event_guide = event_guides.get(period_info.hall_id)
            if not event_guide:
                log.debug(u"Can't find event_guide for ticket hall {}".format(period_info.hall_id))
                continue

            period = self.create_period(event_guide, period_info)
            self.create_sessions(period, period_info)

    def disable_signals(self):
        """"""

        post_save.disconnect(update_cache_table, sender=m.EventGuide)
        post_save.disconnect(update_cache_table, sender=m.Period)

        log.debug('Signals were disabled')

    def enable_signals(self):
        """"""

        post_save.connect(update_cache_table, sender=m.EventGuide)
        post_save.connect(update_cache_table, sender=m.Period)

        log.debug('Signals were enabled')

    def parse_halls(self):
        """Return our halls for ticket sessions"""

        hall_ids = self._ticket_sessions.values_list('hall', flat=True).distinct()
        hall_ids = filter(None, hall_ids)

        halls = (
            self.HALL_MODEL.objects
                .filter(id__in=hall_ids, hall__isnull=False)
                .select_related('hall', 'hall__guide')
        )

        return halls

    def remove_event_guides(self):
        """Remove event guides for event"""

        m.EventGuide.objects.filter(event=self._event, source=self.SOURCE).delete()
        log.debug('Remove event_guides for event: {}'.format(self._event))

    def create_event_guides(self):
        """
        Create EventGuide models

        :return: dict ticket_hall => event_guide
        """

        ticket_halls = self.parse_halls()

        event_guides = []
        for ticket_hall in ticket_halls:
            hall = ticket_hall.hall
            guide = hall.guide
            event_guide, created = m.EventGuide.objects.get_or_create(
                guide=guide, hall=hall, event=self._event, source=self.SOURCE, defaults=dict(
                    guide_name=guide.title_short,
                )
            )
            # Add binding with ticket_hall
            event_guide.ticket_hall = ticket_hall
            event_guides.append(event_guide)
            if created:
                log.debug('Add new event_guide: {}'.format(event_guide))

        return {eg.ticket_hall.id: eg for eg in event_guides}
