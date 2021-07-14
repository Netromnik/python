# -*- coding: utf-8 -*-

import datetime
import random

from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.test.client import RequestFactory
from django_dynamic_fixture import G

from irk.afisha.models import Event, EventType, Genre, Guide, EventGuide, \
    Period, Sessions, CurrentSession, Announcement
from irk.afisha.templatetags.afisha_tags import announce_slider
from irk.afisha.tests.utils import create_event
from irk.tests.unit_base import UnitTestBase
from irk.utils.helpers import inttoip, time_combine


class CurrentSessionTestCase(UnitTestBase):
    """ Тестирование наполнения и работы денормализированнной таблицы
        событий
    """

    def setUp(self):
        super(CurrentSessionTestCase, self).setUp()
        self.event_type = G(EventType, alias='night')
        self.event_type_cinema = G(EventType, alias='cinema')

    def test_filling(self):
        """ Тест наполнения
            Создаем событие с сеансами и проверяем соответствие в денормализованной таблице
        """

        date = datetime.date.today() + datetime.timedelta(1)
        genre = G(Genre)
        guide = G(Guide, event_type=self.event_type)

        event = G(Event, type=self.event_type, genre=genre, is_hidden=False)
        event_guide = G(EventGuide, event=event, guide=guide)

        period = G(Period, event_guide=event_guide, duration=None, start_date=date, end_date=date)
        session = G(Sessions, period=period, time=datetime.time(12, 0))

        sessions = CurrentSession.objects.all()

        self.assertEqual(1, sessions.count())
        self.assertEqual(session.time, sessions[0].time)
        self.assertEqual(self.event_type, sessions[0].event_type)
        self.assertEqual(sessions[0].real_date, sessions[0].end_date)  # Не указана длительность, поэтому они равны

        event.type = self.event_type_cinema
        event.save()

        sessions = CurrentSession.objects.all()

        self.assertEqual(1, sessions.count())
        self.assertEqual(self.event_type_cinema, sessions[0].event_type)

        period.duration = datetime.time(5, 0, 0)
        period.save()

        sessions = CurrentSession.objects.all()

        self.assertEqual(1, sessions.count())
        self.assertEqual(sessions[0].end_date, (time_combine(sessions[0].real_date, period.duration)))

    def test_night_sessions(self):
        """
            Проверяем ночные сеансы. т.е. сеансы 0-6 часов показываются сегодня после сеансов 6-0
        """
        date = datetime.date.today() + datetime.timedelta(1)

        genre = G(Genre)
        guide = G(Guide, event_type=self.event_type)
        event = G(Event, type=self.event_type, genre=genre, parent=None, is_hidden=False)
        event_guide = G(EventGuide, event=event, guide=guide, hall=None)
        period = G(Period, event_guide=event_guide, start_date=date, end_date=date, duration=None)
        G(Sessions, period=period, time=datetime.time(1, 0))
        G(Sessions, period=period, time=datetime.time(23, 0))
        page = self.app.get(reverse('afisha:index'))
        self.assertEqual(event, page.context['object_list'][0])
        # Проверяем что последний сеанс нулевой привязки 1:00
        schedule = page.context['object_list'][0].schedule

        self.assertEqual(datetime.time(1, 0), schedule.sessions[0].time)

    def test_cinema_night_sessions(self):

        date = datetime.date.today() + datetime.timedelta(1)

        genre = G(Genre)
        guide = G(Guide, event_type=self.event_type_cinema)
        event = G(Event, type=self.event_type_cinema, genre=genre, parent=None, is_hidden=False)
        event_guide = G(EventGuide, event=event, guide=guide, hall=None)
        period = G(Period, event_guide=event_guide, start_date=datetime.date.today(), end_date=date, duration=None)
        G(Sessions, period=period, time=datetime.time(1, 0))
        G(Sessions, period=period, time=datetime.time(20, 0))

        context = self.app.get(reverse('afisha:events_type_index', args=(self.event_type_cinema.alias, ))).context
        self.assertEqual(event, context['object_list'][0])
        sessions = context['object_list'][0].schedule[0]['sessions']

        # Если системное время больше 20:00, то в расписании сеансов должен отображаться только сеанс в 01:00
        if datetime.datetime.now().time() > datetime.time(20, 0):
            self.assertEqual(datetime.time(1, 0), sessions[0].time)
        else:
            self.assertEqual(datetime.time(20, 0), sessions[0].time)
            self.assertEqual(datetime.time(1, 0), sessions[1].time)

    def test_session_none(self):
        """ Тестирование событий, для которых сеансы уточняются """
        date = datetime.date.today() + datetime.timedelta(1)
        genre = G(Genre)
        guide = G(Guide, event_type=self.event_type)

        event = G(Event, type=self.event_type, genre=genre, is_hidden=False)
        event_guide = G(EventGuide, event=event, guide=guide)
        G(Period, event_guide=event_guide, duration=None, start_date=date, end_date=date)
        sessions = CurrentSession.objects.all()
        self.assertEqual(1, sessions.count())
        self.assertEqual(None, sessions[0].time)

    def test_past_sessions(self):
        now = datetime.datetime.now()

        genre = G(Genre)
        guide = G(Guide, event_type=self.event_type, guide_ptr__event_type=self.event_type)

        event = G(Event, type=self.event_type, genre=genre, parent=None, is_hidden=False)
        event_guide = G(EventGuide, event=event, guide=guide, hall=None)
        period = G(Period, event_guide=event_guide, start_date=now.date(), end_date=now.date(), duration=None)
        G(Sessions, period=period, time=datetime.time(now.hour - 1, 0))
        next_session = G(Sessions, period=period, time=datetime.time(now.hour + 2, 0))
        page = self.app.get(reverse('afisha:events_type_index', kwargs={'event_type': self.event_type.alias}))
        self.assertEqual(1, len(page.context['object_list']))
        self.assertEqual(next_session.time, page.context['object_list'][0].schedule.first.time)


class EventsTestCase(UnitTestBase):
    """ Тестирование страниц событий """

    def setUp(self):
        super(EventsTestCase, self).setUp()
        G(EventType, alias='culture')
        self.event_type = G(EventType, alias='night', hide_past=True)  # Прошедшие вечеринки должны быть скрыты
        self.event_type_cinema = G(EventType, alias='cinema', on_index=False)  # Кина нет на индексе

    def test_index(self):
        """ Тестирование главной и индексных страниц типов """

        date = datetime.date.today()
        index_events = []
        for event_type in EventType.objects.all():
            genre = G(Genre)
            guide = G(Guide, event_type=event_type, guide_ptr__event_type=event_type)
            event = G(Event, type=event_type, genre=genre, parent=None, is_hidden=False)
            event_guide = G(EventGuide, event=event, guide=guide, hall=None)
            period = G(Period, event_guide=event_guide,
                         start_date=date, end_date=date, duration=None)
            G(Sessions, period=period, time=datetime.time(random.randrange(0, 5), 0))
            if event_type.alias != 'cinema':
                index_events.append(event)

        page = self.app.get(reverse('afisha:index'))

        self.assertFalse(page.context['is_paginated'])
        self.assertEqual(len(index_events), len(page.context['object_list']))

        for event_type in EventType.objects.all():
            page = self.app.get(reverse('afisha:events_type_index', kwargs={'event_type': event_type.alias}))
            self.assertEqual(1, len(page.context['object_list']), "events on %s index" % event_type.alias)

    def test_search(self):
        """Smoke-тест поиска"""

        url = reverse('afisha:search')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'afisha/search.html')

    def test_announcement(self):
        """ Тестирование события без гида """

        date = datetime.date.today()

        genre = G(Genre)
        guide = G(Guide, event_type=self.event_type)
        event = G(Event, type=self.event_type, genre=genre, parent=None, is_hidden=False)
        G(Announcement, event=event, place=None, start=date, end=date + datetime.timedelta(days=5))
        event_guide = G(EventGuide, event=event, guide=guide, hall=None)
        G(Period, event_guide=event_guide, start_date=date, end_date=date, duration=None)

        request = RequestFactory().request()
        request.user = self.create_user('user')
        context = RequestContext(request, {'request': request})
        result = announce_slider(context)
        self.assertEqual(1, len(result['announce_list']))
        self.assertEqual(event, result['announce_list'][0])

        result = announce_slider(context, event_type=self.event_type)
        self.assertEqual(1, len(result['announce_list']))
        self.assertEqual(event, result['announce_list'][0])

        result = announce_slider(context, event_type=self.event_type_cinema)
        self.assertEqual(0, len(result['announce_list']))

    def test_past_date(self):

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(1)
        tomorrow = today + datetime.timedelta(1)
        for event_type in EventType.objects.filter(alias__in=['night', 'culture', 'cinema']):
            genre = G(Genre)
            guide = G(Guide, event_type=event_type)
            event = G(Event, type=event_type, genre=genre, parent=None, announcement=True, main_announcement=True, is_hidden=False)
            event_guide = G(EventGuide, event=event, guide=guide, hall=None)
            G(Period, event_guide=event_guide, start_date=yesterday, end_date=tomorrow, duration=None)

            def get_url(date):
                return reverse('afish:event_read', kwargs={
                    'event_id': event.pk,
                    'year': date.year,
                    'month': '%02d' % date.month,
                    'day': '%02d' % date.day,
                    'event_type': event_type.alias,
                })

            if event_type.alias == 'night':
                self.assertEqual(404, self.app.get(get_url(yesterday), status=404).status_code)
            elif event_type.alias == 'culture':
                response = self.app.get(get_url(yesterday))
                self.assertEqual(200, response.status_code)
                self.assertTemplateUsed(response, 'afisha/event/read.html')
            elif event_type.alias == 'cinema':
                response = self.app.get(get_url(yesterday))
                self.assertEqual(200, response.status_code)
                self.assertTemplateUsed(response, 'afisha/cinema/read.html')
            self.assertEqual(200, self.app.get(get_url(today)).status_code)
            self.assertEqual(200, self.app.get(get_url(tomorrow)).status_code)


class EventCreateTestCase(UnitTestBase):

    def test(self):
        title = self.random_text(20)
        event_type = G(EventType, alias='night')

        form = self.app.get(reverse('afisha:event_create')).forms['form-afisha-event-create']
        form['title'] = title
        form['date'] = datetime.date.today().strftime('%d.%m.%Y')
        form['time'] = '16:52'
        form['place'] = u'Живой звук'
        form['type'] = event_type.id

        form.submit().follow()

        event = Event.objects.get(title=title)

        self.assertTrue(event.is_user_added)
        self.assertTrue(event.is_hidden)
        # Между созданием и проверкой пройдет некоторое время, поэтому хотя бы проверим дату
        self.assertEqual(datetime.date.today(), event.created.date())
        # Тест может выполняться на удаленной машине. Стоит проверять его?
        self.assertEqual(inttoip(event.author_ip), '127.0.0.1')

        page = self.app.get(reverse('afisha:events_type_index', kwargs={'event_type': event_type.alias}))
        self.assertEqual(0, len(page.context['object_list']))

        response = self.app.get(event.get_absolute_url(), status=404)
        self.assertEqual(response.status_code, 404)  # Событие не отображается до модерации

        event.is_hidden = False  # Одобрено модератором
        event.save()

        response = self.app.get(event.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # Событие видно всем


class EventsFiltersTestCase(UnitTestBase):
    """ Тестирование фильтров  """

    def test_time_filters(self):
        date = datetime.date.today() + datetime.timedelta(1)
        genre = G(Genre)
        event_type = G(EventType, alias='night')
        guide = G(Guide, event_type=event_type)

        event = G(Event, type=event_type, genre=genre, is_hidden=False)
        event_guide = G(EventGuide, event=event, guide=guide)
        period = G(Period, event_guide=event_guide, start_date=date, end_date=date, duration=datetime.time(5, 30))
        G(Sessions, period=period, time=datetime.time(10, 0))

        page = self.app.get("%s?time=morning" % reverse('afisha:events_list'))
        self.assertEqual(1, len(page.context['object_list']))


class CountBuyButtonClickTest(UnitTestBase):
    """Тестирование подсчета нажатий на кнопку «Купить билет»"""

    csrf_checks = False

    def setUp(self):
        self.url = reverse('afisha:buy_button_click')
        self.event = create_event()

    def test_success(self):
        """Успешное обновление счетчика"""

        data = {
            'event_id': self.event.id
        }

        self.assertEqual(0, Event.objects.get(id=self.event.id).buy_btn_clicks)
        response = self.ajax_post(self.url, data)
        self.assertTrue(response.json['ok'])
        self.assertEqual(1, Event.objects.get(id=self.event.id).buy_btn_clicks)

    def test_not_event_id_param(self):
        """Нет параметра с id события"""

        data = {
            'xxx': self.event.id
        }

        self.assertEqual(0, Event.objects.get(id=self.event.id).buy_btn_clicks)
        response = self.ajax_post(self.url, data)
        self.assertFalse(response.json['ok'])
        self.assertEqual(0, Event.objects.get(id=self.event.id).buy_btn_clicks)

    def test_invalid_event_id(self):
        """Неверный event_id"""

        data = {
            'event_id': 100500,
        }

        response = self.ajax_post(self.url, data)
        self.assertFalse(response.json['ok'])
