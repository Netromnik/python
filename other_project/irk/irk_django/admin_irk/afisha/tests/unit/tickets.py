# -*- coding: utf-8 -*-
# Тесты классов для работы с системой kassy.ru

import datetime

from django_dynamic_fixture import G, N

from django.db import transaction

from irk.afisha import models as m
from irk.afisha.tickets.binder import TicketBinder
from irk.afisha.tickets.helpers import correct_night_session
from irk.afisha.tickets.kinomax import KinomaxTicketCreator
from irk.afisha.tickets.rambler import RamblerTicketCreator
from irk.tests.unit_base import UnitTestBase


class TicketTestMixin(object):
    """Миксин для тестирования классов билетных систем"""

    label = ''
    building_model = None
    hall_model = None
    event_model = None
    session_model = None

    def setUp(self):
        self._guide = G(m.Guide)
        self._hall = G(m.Hall, guide=self._guide)
        self._ticket_building = G(self.building_model, guide=self._guide)
        self._ticket_hall = G(self.hall_model, building=self._ticket_building, hall=self._hall)

    def assert_bind(self, ticket_session):
        filters = {
            '{}session'.format(self.label): ticket_session
        }
        self.assertTrue(
            m.CurrentSession.objects.filter(**filters).exists(),
            msg=u'{}_session {} is not binded'.format(self.label, ticket_session.pk)
        )

    def assert_not_bind(self, ticket_session):
        filters = {
            '{}session'.format(self.label): ticket_session
        }
        self.assertFalse(
            m.CurrentSession.objects.filter(**filters).exists(),
            msg=u'{}_session {} is binded'.format(self.label, ticket_session.pk)
        )

    def _create_event(self, **kwargs):
        """Создать событие"""

        return G(m.Event, is_hidden=False, **kwargs)

    def _create_current_sessions(self, event, count=5, start_stamp=None):
        """Создать сеансы для события"""

        start_stamp = start_stamp or datetime.datetime.now()

        sessions_stamps = [start_stamp + datetime.timedelta(days=i) for i in range(1, count+1)]
        for stamp in sessions_stamps:
            self._create_current_session(event, stamp=stamp)

    def _create_current_session(self, event, stamp):
        """Создать конкретный сеанс для события"""

        return G(
            m.CurrentSession, event=event, date=stamp.date(), time=stamp.time(), fake_date=stamp, guide=self._guide,
            hall=self._hall
        )

    def _create_ticket_event(self, event=None):
        """Создать событие в билетной системе"""

        return G(self.event_model, event=event)

    def _create_ticket_sessions(self, ticket_event, count=5, start_stamp=None):
        """
        Создать сеансы в билетной системе
        """

        start_stamp = start_stamp or datetime.datetime.now()

        sessions_stamps = [start_stamp + datetime.timedelta(days=i) for i in range(1, count+1)]
        ticket_sessions = []
        for stamp in sessions_stamps:
            ticket_sessions.append(
                self._create_ticket_session(ticket_event, stamp=stamp)
            )

        return ticket_sessions

    def _create_ticket_sessions_from_current_sessions(self, ticket_event, bind=False):
        """
        Создать сеансы в билетной системе из текущих сеансов

        :param bool bind: если True привязывается соответствующий сеанс
        """

        ticket_sessions = []
        for cs in ticket_event.event.currentsession_set.all():
            ticket_sessions.append(
                self._create_ticket_session(ticket_event, cs.fake_date, cs if bind else None)
            )

        return ticket_sessions

    def _create_ticket_session(self, ticket_event, stamp, current_session=None):
        """
        Создать сеанс в билетной системе.
        Если передан current_session, то созданный сеанс сразу привязывается нему.
        """

        ticket_session = N(
            self.session_model, event=ticket_event, current_session=None, hall=self._ticket_hall,
            datetime=stamp, show_datetime=correct_night_session(stamp)
        )

        if current_session:
            ticket_session.current_session = current_session

        ticket_session.save()

        return ticket_session


class TicketBinderTestMixin(TicketTestMixin):
    """Тесты связывателя сеансов"""

    def setUp(self):
        super(TicketBinderTestMixin, self).setUp()
        self._binder = TicketBinder(self.label)

    def test_bind(self):
        """Проверка связывания сеансов для конкретного события"""

        event = self._create_event()
        self._create_current_sessions(event)
        ticket_event = self._create_ticket_event(event)
        ticket_sessions = self._create_ticket_sessions_from_current_sessions(ticket_event)

        self._binder.bind(ticket_event)

        for ticket_session in ticket_sessions:
            self.assert_bind(ticket_session)
            
    def test_unbind(self):
        """Проверка отвязывания сеансов"""

        event = self._create_event()
        self._create_current_sessions(event)
        ticket_event = self._create_ticket_event(event)
        ticket_sessions = self._create_ticket_sessions_from_current_sessions(ticket_event, bind=True)

        self._binder.unbind(ticket_event)

        for ticket_session in ticket_sessions:
            self.assert_not_bind(ticket_session)

    def test_update(self):
        """
        Обновление сеансов для события

        Берем событие с привязкой, добавляем сеанс, вызываем функциию, проверяем что новые сеансы привязались
        """

        event = self._create_event()
        self._create_current_sessions(event)
        ticket_event = self._create_ticket_event(event)
        ticket_sessions = self._create_ticket_sessions_from_current_sessions(ticket_event, bind=True)

        # Удаляем первый сеанс
        first_ticket_session = ticket_sessions.pop(0)
        first_ticket_session.delete()
        # Добавляем еще один сеанс
        cs = self._create_current_session(event, stamp=datetime.datetime.now() + datetime.timedelta(days=10))
        ticket_sessions.append(self._create_ticket_session(ticket_event, cs.fake_date))

        self._binder.update(ticket_event)

        for ticket_session in ticket_sessions:
            self.assert_bind(ticket_session)

    def test_update_when_current_session_is_changed(self):
        """Обновление сеансов для события, когда текущий сеанс изменился"""

        event = self._create_event()
        self._create_current_sessions(event)
        ticket_event = self._create_ticket_event(event)
        self._create_ticket_sessions_from_current_sessions(ticket_event, bind=True)

        # Меняем расписание одного из сеансов
        cs = event.currentsession_set.first()
        stamp = datetime.datetime.now()
        cs.date = stamp.date()
        cs.time = stamp.time()
        cs.fake_date = stamp
        cs.save()
        # Создаем в билетной системе соответствующий сеанс.
        ticket_session = self._create_ticket_session(ticket_event, cs.fake_date)

        self.assert_not_bind(ticket_session)
        with transaction.atomic():
            self._binder.update(ticket_event)
        self.assert_bind(ticket_session)


class KassyBinderTest(TicketBinderTestMixin, UnitTestBase):
    label = 'kassy'
    building_model = m.KassyBuilding
    hall_model = m.KassyHall
    event_model = m.KassyEvent
    session_model = m.KassySession


class RamblerBinderTest(TicketBinderTestMixin, UnitTestBase):
    label = 'rambler'
    building_model = m.RamblerBuilding
    hall_model = m.RamblerHall
    event_model = m.RamblerEvent
    session_model = m.RamblerSession


class KinomaxBinderTest(TicketBinderTestMixin, UnitTestBase):
    label = 'kinomax'
    building_model = m.KinomaxBuilding
    hall_model = m.KinomaxHall
    event_model = m.KinomaxEvent
    session_model = m.KinomaxSession


class TicketCreatorTestMixin(TicketTestMixin):
    """Тесты создателя сеансов"""

    creator_class = None

    def test_create(self):
        """Создание сеансов для события"""

        event = self._create_event()
        ticket_event = self._create_ticket_event(event)
        self._create_ticket_sessions(ticket_event, 10)

        creator = self.creator_class()
        creator.create(ticket_event)

        self.assertEqual(10, event.currentsession_set.count())

    def test_create_all_binding_events(self):
        """Создание сеансов для всех связанных событий"""

        events = [self._create_event() for _ in range(5)]
        for event in events:
            ticket_event = self._create_ticket_event(event)
            self._create_ticket_sessions(ticket_event, 10)

        with transaction.atomic():
            creator = self.creator_class()
            creator.create_for_all_events()

        for event in events:
            self.assertEqual(10, event.currentsession_set.count())

    def test_update_events_which_were_removed_from_ticket_system(self):
        """Обновление событий которые были удалены из билетной системы"""

        event = self._create_event()
        ticket_event = self._create_ticket_event(event)
        today = datetime.datetime.now()
        self._create_ticket_sessions(ticket_event, count=10, start_stamp=today)

        creator = self.creator_class()
        creator.create(ticket_event)

        stamp = (today + datetime.timedelta(days=2)).date()
        self.assertEqual(10, event.currentsession_set.count())
        self.assertTrue(event.currentsession_set.filter(date=stamp).exists())

        # Допустим, что сеансы для даты stamp отменили
        ticket_event.sessions.filter(datetime__day=stamp.day, datetime__month=stamp.month).delete()
        creator.create(ticket_event)
        self.assertFalse(event.currentsession_set.filter(date=stamp).exists())


class RamblerTicketCreatorTest(TicketCreatorTestMixin, UnitTestBase):
    label = 'rambler'
    building_model = m.RamblerBuilding
    hall_model = m.RamblerHall
    event_model = m.RamblerEvent
    session_model = m.RamblerSession
    creator_class = RamblerTicketCreator


class KinomaxTicketCreatorTest(TicketCreatorTestMixin, UnitTestBase):
    label = 'kinomax'
    building_model = m.KinomaxBuilding
    hall_model = m.KinomaxHall
    event_model = m.KinomaxEvent
    session_model = m.KinomaxSession
    creator_class = KinomaxTicketCreator
