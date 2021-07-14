# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime
import logging
import re
import xml.etree.ElementTree as ET
from collections import namedtuple
from itertools import groupby

import requests

from django.core.exceptions import ObjectDoesNotExist

from irk.afisha import models as m
from irk.afisha.settings import KINOMAX_CINEMA_IDS, KINOMAX_DAYS
from irk.afisha.tickets.creator import TicketCreator
from irk.afisha.tickets.helpers import correct_night_session, create_afisha_import_logger
from irk.utils.helpers import float_or_none, int_or_none

log = logging.getLogger(__name__)
import_log = create_afisha_import_logger('kinomax')


class KinomaxGrabber(object):
    """
    Граббер сеансов из системы kinomax
    """

    cinema_ids = KINOMAX_CINEMA_IDS
    days = KINOMAX_DAYS

    def run(self):
        """Запустить граббер"""

        base = datetime.datetime.today()
        date_list = [base + datetime.timedelta(days=x) for x in range(0, self.days)]
        updated_sessions = set()

        for cinema_id in self.cinema_ids:
            for date in date_list:
                # Парсинг расписания кинотеатра на конкретную дату
                try:
                    response = requests.get(self._make_url(cinema_id, date))
                except requests.exceptions.RequestException as e:
                    import_log.error('Невозможно сделать запрос к API')
                    raise e

                try:
                    root = ET.fromstring(response.content)
                except ET.ParseError as e:
                    import_log.error('Неверный ответ API')
                    raise e

                building = self._parse_building(root)
                movies = root.findall('movies/movie')
                for movie in movies:
                    event = self._parse_event(movie)
                    sessions = movie.findall('schedule/session')
                    for session in sessions:
                        hall = self._parse_hall(session, building)
                        session = self._parse_session(session, event, hall, date)
                        updated_sessions.add(session.id)

        self._clean_sessions(updated_sessions)
        self._fill_date_start()

        log.info('События с kinomax успешно загружены.')

        # Принудительная отправка лога при завершении работы парсера
        import_log.handlers[0].flush()

    def _make_url(self, cinema_id, date=None):
        """Формирование url"""
        if not date:
            date = datetime.date.today()
        date_text = date.strftime('%Y-%m-%d')

        return 'http://api.kinomax.ru/export/schedule?cinema={}&date={}'.format(cinema_id, date_text)

    def _parse_event(self, movie):
        """Импорт фильмов"""

        event, created = m.KinomaxEvent.objects.update_or_create(
            id=movie.attrib['id'], defaults={
                'title': movie.find('name').text or '',
                'duration': int_or_none(movie.find('length').text),
                'rating': float_or_none(movie.find('rating').text),
                'votes': int_or_none(movie.find('rating').attrib['votes']),
                'description': movie.find('description').text or '',
                'cast': movie.find('cast').text or '',
                'genres': movie.find('genres').text or '',
                'director': movie.find('director').text or '',
                'trailer': movie.find('trailer').text or '',
                'image': movie.find('frameUrl').text or '',
            }
        )

        if created:
            log.debug('Add new event from kinomax: {}'.format(event))
            import_log.info('Добавлено новое событие "{}"'.format(event.title))

        return event

    def _parse_session(self, session, event, hall, date):
        """Импорт сеанс"""
        time = datetime.datetime.strptime(session.attrib['time'], '%H:%M').time()
        timestamp = datetime.datetime.combine(date, time)
        show_timestamp = correct_night_session(timestamp) if timestamp is not None else None

        kinomax_session, created = m.KinomaxSession.objects.update_or_create(
            id=session.attrib['id'], defaults={
                'event': event,
                'hall': hall,
                'price': session.find('priceRange').text or '',
                'datetime': timestamp,
                'show_datetime': show_timestamp,
                'type': session.find('type').attrib['id'] or '',
            }
        )

        if created:
            log.debug('Add new session from kinomax: {}'.format(kinomax_session))

        return kinomax_session

    def _parse_building(self, root):
        """Получить учреждение"""

        building, created = m.KinomaxBuilding.objects.update_or_create(
            id=root.find('cinema').attrib['id'], defaults={
                'token': root.find('cinema').attrib['token'] or '',
                'title': root.find('cinema').text or '',
            }
        )

        if created:
            log.debug('Add new building from kinomax: {}'.format(building))
            import_log.info('Добавлено новое заведение "{}"'.format(building.title))
        return building

    def _parse_hall(self, session, building):
        """Получить зал"""

        hall, created = m.KinomaxHall.objects.update_or_create(
            building=building,
            title=session.find('hall').text or '',
        )

        if created:
            log.debug('Add new hall from kinomax: {}'.format(hall))
            import_log.info('Добавлен новый зал "{}" для заведения "{}"'.format(hall.title, hall.building.title))
        return hall

    def _fill_date_start(self):
        """Заполнить поле «дата начала» у событий"""

        for event in m.KinomaxEvent.objects.filter(date_start__isnull=True):
            try:
                session = event.sessions.earliest()
                event.date_start = session.datetime
                event.save(update_fields=['date_start'])
            except ObjectDoesNotExist:
                pass

    def _clean_sessions(self, updated_sessions):
        """Clean invalid sessions"""

        log.debug('Deleting invalid sessions')
        invalid_sessions = m.KinomaxSession.objects.exclude(id__in=updated_sessions)
        count = invalid_sessions.count()
        if count:
            invalid_sessions.delete()
            log.info('{} invalid sessions deleted'.format(count))


class KinomaxTicketCreator(TicketCreator):
    HALL_MODEL = m.KinomaxHall
    EVENT_MODEL = m.KinomaxEvent
    SOURCE = m.EventGuide.SOURCE_KINOMAX

    def parse_periods(self):
        """Return periods for ticket sessions"""

        sessions = self._ticket_sessions.order_by('hall', 'price', 'type', 'show_datetime')

        PeriodInfo = namedtuple('PeriodInfo', 'hall_id date times price is_3d')

        for key, group in groupby(sessions, lambda s: (s.hall_id, s.price, s.type.upper() == '3D')):
            hall_id, price, is_3d = key
            for date, items in groupby(group, lambda s: s.show_datetime.date()):
                times = list(i.show_datetime.time() for i in items)
                yield PeriodInfo(hall_id, date, times, price, is_3d)

    def create_period(self, event_guide, period_info):
        """Create single period"""

        period, created = m.Period.objects.get_or_create(
            event_guide=event_guide,
            start_date=period_info.date,
            end_date=period_info.date,
            defaults=dict(
                price=self._parse_price(period_info.price),
                is_3d=period_info.is_3d,
            ))
        if created:
            log.debug(u'Add new period: {}'.format(period.id))

        return period

    def create_sessions(self, period, period_info):
        """Create sessions for period by times"""

        for time in period_info.times:
            session, created = m.Sessions.objects.get_or_create(
                period=period, time=time, price=self._parse_price(period_info.price),
            )
            if created:
                log.debug('Add new session: {}'.format(session.id))

    def _parse_price(self, value):
        """Return human readable text for price"""

        try:
            value = re.search(r'(\d+)', value).group()
        except (AttributeError, TypeError):
            return ''
        else:
            return u'от {} руб.'.format(value)

    def _parse_duration(self, value):
        """
        Return datetime.time from minutes

        >>> self._parse_duration(150)
        >>> datetime.time(2, 30)
        >>> self._parse_duration(None)
        >>>
        """
        try:
            value = datetime.time(*divmod(value, 60))
        except TypeError:
            return None
        else:
            return value
