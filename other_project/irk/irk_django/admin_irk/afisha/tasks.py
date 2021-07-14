# -*- coding: utf-8 -*-

import logging

from irk.afisha.models import Event
from irk.afisha.tickets.binder import TicketBinder, get_ticket_event
from irk.afisha.tickets.creator import get_ticket_creator
from irk.afisha.tickets.kassy import KassyGrabber
from irk.afisha.tickets.kinomax import KinomaxGrabber
from irk.afisha.tickets.rambler import RamblerGrabber
from irk.utils.grabber import proxy_requests
from irk.utils.tasks.helpers import make_command_task, task

logger = logging.getLogger(__name__)


afisha_clean_cache = make_command_task('afisha_clean_cache')

afisha_hide_old_events = make_command_task('afisha_hide_old_events')


@task(ignore_result=True)
def bind_ticket_sessions(label, ticket_event_id):
    """Задача на привязку к событию сеансов"""

    ticket_event = get_ticket_event(label, ticket_event_id)
    if not ticket_event:
        logger.error('Not found {} event with id {}'.format(label, ticket_event_id))
        return

    # Для Rambler.Kassa и Kinomax создаем сеансы на основе данных из билетных систем
    if label in ('rambler', ):
        creator = get_ticket_creator(label)
        creator.create(ticket_event)

    binder = TicketBinder(label)
    binder.bind(ticket_event)


@task(ignore_result=True)
def unbind_ticket_sessions(label, ticket_event_id):
    """Задача на отвязку сеансов"""

    ticket_event = get_ticket_event(label, ticket_event_id)
    if not ticket_event:
        logger.error('Not found {} event with id {}'.format(label, ticket_event_id))
        return

    binder = TicketBinder(label)
    binder.unbind(ticket_event)


@task(ignore_result=True)
def run_kassy_grabber():
    """Запуск граббера билетной системы kassy.ru"""

    grabber = KassyGrabber()
    grabber.run()

    binder = TicketBinder('kassy')
    binder.update_all_events()


@task(ignore_result=True)
def run_rambler_grabber():
    """Запуск граббера билетной системы Rambler.Kassa"""

    grabber = RamblerGrabber()
    grabber.run()

    creator = get_ticket_creator('rambler')
    creator.create_for_all_events()

    binder = TicketBinder('rambler')
    binder.update_all_events()


@task(ignore_result=True)
def run_kinomax_grabber():
    """Запуск граббера билетной системы Kinomax"""

    grabber = KinomaxGrabber()
    grabber.run()

    creator = get_ticket_creator('kinomax')
    creator.create_for_all_events()

    binder = TicketBinder('kinomax')
    binder.update_all_events()
