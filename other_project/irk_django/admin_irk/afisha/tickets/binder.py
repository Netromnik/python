# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from irk.afisha import models as m

log = logging.getLogger(__name__)

EVENT_MODEL_MAP = {
    'kassy': m.KassyEvent,
    'rambler': m.RamblerEvent,
}


def get_ticket_event(label, ticket_event_id):
    """Return ticket event object by label and id"""

    event_class = EVENT_MODEL_MAP.get(label)
    if not event_class:
        log.error('Not found {} event class'.format(label))
        return None

    return event_class.objects.filter(id=ticket_event_id).first()


class TicketBinder(object):
    """Binder class for ticket system binders"""

    def __init__(self, label):
        self.label = label
        self.model_event = EVENT_MODEL_MAP.get(label)

    def bind(self, ticket_event):
        """Bind ticket system session with our current sessions"""
        for session in ticket_event.sessions.filter(is_ignore=False):
            cs = self.get_current_session(session)
            if not cs:
                log.error('Not found current session for {} session with id {}'.format(
                    self.label, session.id
                ))
                continue

            session.current_session = cs
            try:
                session.save(update_fields=['current_session'])
            except IntegrityError as err:
                log.error('Failed bind current_session {} to {} session {}. More: {}'.format(
                    cs.id, self.label, session.id, err
                ))
                continue

            log.info('{} session {} bound to current session {}'.format(
                self.label.title(), session.pk, cs.pk
            ))

    def unbind(self, ticket_event):
        """Unbind ticket system sessions"""

        ticket_event.sessions.update(current_session=None)

    def update_all_events(self):
        """
        Обновить информацию по сеансам для всех событий.

        Ранее привязанные сеансы удаляются!
        """
        log.info('Updating {} events'.format(self.label))

        ticket_events = self.model_event.objects.filter(event__isnull=False, event__is_hidden=False)

        for ticket_event in ticket_events.iterator():
            log.debug('Processing {} event {}'.format(self.label, ticket_event.pk))
            self.update(ticket_event)

        log.info('{} events updated'.format(self.label.title()))

    def update(self, ticket_event):
        """Update bindings for ticket event"""
        self.unbind(ticket_event)
        self.bind(ticket_event)
        log.debug('{} event {} successfully updated'.format(self.label.title(), ticket_event.id))

    def get_ticket_event(self, ticket_event_id):
        """Return ticket event by id"""

        ticket_event = self.model_event.objects.filter(id=ticket_event_id).first()
        return ticket_event

    def get_current_session(self, session):
        """Return respective current session"""
        filters = {
            'fake_date': session.show_datetime or session.datetime
        }
        # Для кассы.ру сессия связывается по заведению и дате
        if self.label == 'kassy':
            guide = self._get_guide(session)
            if not guide:
                log.debug('Not found guide for {} session {}'.format(self.label, session.id))
                return
            filters.update({
                'guide': guide,
            })
        # для остальных по залу и дате
        else:
            hall = self._get_hall(session)
            if not hall:
                log.debug('Not found hall for {} session {}'.format(self.label, session.id))
                return
            filters.update({
                'hall': hall,
            })

        cs = session.event.event.currentsession_set.filter(**filters).first()

        return cs

    def _get_hall(self, ticket_session):
        """Return hall"""

        try:
            hall = ticket_session.hall.hall
        except ObjectDoesNotExist:
            return
        else:
            return hall

    def _get_guide(self, ticket_session):
        """Return guide"""

        try:
            ticket_hall = ticket_session.hall
            ticket_building = ticket_hall.building
            # Для касс.ру отдельная проверка на органный зал
            if (
                self.label == 'kassy' and
                ticket_building.title == u'Филармония' and
                ticket_hall.title == u'Органный зал'
            ):
                guide = m.Guide.objects.filter(title_short=u'Органный зал').first()
            else:
                guide = ticket_building.guide
        except ObjectDoesNotExist:
            log.error("Can't find guide for {} session with id {}".format(self.label, ticket_session.id))
            return None
        else:
            return guide
