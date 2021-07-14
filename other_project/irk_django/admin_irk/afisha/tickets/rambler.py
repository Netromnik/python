# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import io
import json
import logging
import re
from collections import namedtuple
from itertools import groupby

from six.moves import urllib

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

import irk.afisha.settings as app_settings
from irk.afisha import models as m
from irk.afisha.tickets.creator import TicketCreator
from irk.afisha.tickets.helpers import correct_night_session, create_afisha_import_logger
from irk.utils.grabber import proxy_requests

log = logging.getLogger(__name__)
import_log = create_afisha_import_logger('rambler')


class RamblerApiError(Exception):
    pass


class RamblerApi(object):
    """
    Class for access rambler.kass API

    More info: http://api.kassa.rambler.ru/help
    """

    BASE_URL = 'http://api.kassa.rambler.ru/v2/{api_key}/{format}/'
    TIMEOUT = 10

    def __init__(self, key, format='json'):
        self._key = key
        self._format = format

    def creation_list(self, creation_type='movie', city_id=None, max_date=None):
        """
        Get list of objects of type `creation_type` with schedule and tickets

        :param creation_type: Possible options: Place, Concert, Performance, Movie, Event, SportEvent
        :param city_id: ID of city to filter list
        :param max_date: Return only objects that has schedule with dates less then specified.
        """

        params = {
            'cityId': city_id or app_settings.RAMBLER_CITY_ID,
        }
        if max_date is not None:
            params['maxDate'] = max_date

        path = '{}/list'.format(creation_type)

        return self._request(path, params=params)

    def place_list(self, city_id=None, max_date=None):
        """
        Get list of places (cinemas, concert halls etc) with schedule and tickets

        :param city_id: ID of city to filter list
        :param max_date: Return only objects that has schedule with dates less then specified.
        """

        params = {
            'cityId': city_id or app_settings.RAMBLER_CITY_ID,
        }
        if max_date is not None:
            params['maxDate'] = max_date

        return self._request('place/list', params=params)

    def schedule(
            self, class_type, object_id=None, date_from=None, date_to=None, city_id=None, sale_supported_only=False
    ):
        """
        Get schedule for place or creation with {classType}

        :param class_type: place or creation_types
        :param object_id: filter by object
        :param date_from: Only session with dates later then
        :param date_to: Only session with dates before
        :param city_id: Filter by city
        :param sale_supported_only: if true, method returns only sessions with available tickets, else - all sessions.
        """

        params = {
            'classType': class_type,
            'cityId': city_id or app_settings.RAMBLER_CITY_ID,
            'saleSupportedOnly': sale_supported_only,

        }
        if object_id is not None:
            params['objectID'] = object_id

        if date_from is not None:
            params['dateFrom'] = date_from

        if date_to is not None:
            params['dateTo'] = date_to

        path = '{}/schedule'.format(class_type)

        return self._request(path, params=params)

    def _request(self, path, params=None, method='GET'):
        """
        Construct and send Request. Returns JSON.

        :param path: api endpoint
        :param params: get parameters
        :param method: http method
        :return: json
        :raise: RamblerApiError
        """

        url = urllib.parse.urljoin(self.BASE_URL.format(api_key=self._key, format=self._format), path)

        try:
            response = proxy_requests.request(method, url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
        except proxy_requests.RequestException as err:
            log.error(err)
            import_log.error('Неверный ответ API')
            raise RamblerApiError(err.message)

        data = response.json()

        # Проверять сообщения об ошибках в ответах API
        code = data.get('Code', '')
        message = data.get('Message', '')
        if code or message:
            err_text = 'Code: {}, Message: {}'.format(code, message)
            log.error(err_text)
            import_log.error('Ошибка ответа API, {}'.format(err_text))
            raise RamblerApiError(err_text)

        return data

    def save(self, data, filename):
        """Save data in file with filename"""

        with io.open(filename, 'w') as out:
            out.write(json.dumps(data, indent=4, ensure_ascii=False))


class RamblerGrabber(object):
    """Grabbing data from Rambler.Kassa API and populate Rambler* models"""

    def __init__(self):
        self._api = RamblerApi(app_settings.RAMBLER_API_KEY)

    def run(self):
        """Run grabber"""

        log.debug('Start grabbing Rambler.Kassa')

        self._grab_buildings()
        self._grab_events()
        self._grab_sessions()
        self._fill_date_start()

        log.debug('Finish grabbing Rambler.Kassa')

        # Принудительная отправка лога при завершении работы парсера
        import_log.handlers[0].flush()

    def _grab_buildings(self):
        for data in self._api.place_list().get('List', []):
            building, created = m.RamblerBuilding.objects.update_or_create(
                id=data.get('ObjectID'), defaults=dict(
                    name=data.get('Name', ''),
                    city_id=data.get('CityID', ''),
                    address=data.get('Address', ''),
                    latitude=data.get('Latitude', 0),
                    longitude=data.get('Longitude', 0),
                    rate=data.get('Rate', ''),
                    category=data.get('Category', ''),
                    sale_from=data.get('SaleFrom', ''),
                    sale_for=data.get('SaleFor', ''),
                    cancel_type=data.get('CancelType', ''),
                    cancel_period=data.get('CancelPeriod', 0),
                    is_vvv_enabled=data.get('IsVvvtEnabled', False),
                    has_terminal=data.get('HasTerminal', False),
                    has_print_device=data.get('HasPrintDevice', False),
                    class_type=data.get('ClassType', ''),
                )
            )

            if created:
                log.debug('Add new building from Rambler.Kassa: {}'.format(building))
                import_log.info('Добавлено новое заведение "{}"'.format(building.name))

    def _grab_events(self):
        for data in self._api.creation_list().get('List', []):
            event, created = m.RamblerEvent.objects.update_or_create(
                id=data.get('ObjectID'), defaults=dict(
                    name=data.get('Name', '') or '',
                    original_name=data.get('OriginalName', '') or '',
                    genre=data.get('Genre', '') or '',
                    country=data.get('Country', '') or '',
                    view_count_daily=data.get('ViewCountDaily', 0),
                    age_restriction=data.get('AgeRestriction', '') or '',
                    thumbnail=data.get('Thumbnail', '') or '',
                    horizonal_thumbnail=data.get('HorizonalThumbnail', '') or '',
                    cast=data.get('Cast', '') or '',
                    description=data.get('Description', '') or '',
                    director=data.get('Director', '') or '',
                    creator_name=data.get('CreatorName') or '',
                    creator_id=data.get('CreatorObjectId') or '',
                    year=data.get('Year', '') or '',
                    duration=data.get('Duration', '') or '',
                    is_non_stop=data.get('IsNonStop', True),
                    rating=data.get('Rating', '') or '',
                    class_type=data.get('ClassType', '') or '',
                )
            )

            if created:
                log.debug('Add new event from Rambler.Kassa: {}'.format(event))
                import_log.info('Добавлено новое событие "{}"'.format(event.name))

    def _grab_sessions(self):
        updated_sessions = set()
        for data in self._api.schedule('Movie').get('List', []):
            hall = self._create_hall(data)
            if not hall:
                continue

            event = m.RamblerEvent.objects.filter(id=data.get('CreationObjectID')).first()
            session = self._create_session(data, event, hall)
            updated_sessions.add(session.id)

        self._clean_sessions(updated_sessions)

    def _create_hall(self, data):
        """Create ticket hall"""

        try:
            # Случается, что PlaceObjectID для сессии есть, но его нет в списке мест
            hall, created = m.RamblerHall.objects.update_or_create(
                hallid=data.get('HallID'), building_id=data.get('PlaceObjectID'), defaults=dict(
                    name=data.get('HallName')
                )
            )
            if created:
                log.debug('Add new hall from Rambler.Kassa: {}'.format(hall))
                import_log.info('Добавлен новый зал "{}" для заведения "{}"'.format(hall.name, hall.building.name))

            return hall
        except IntegrityError as err:
            log.error(
                'Cannot create or update hall from Rambler.Kassa. PlaceId: {}, HallId: {}. Origin error: {}'.format(
                    data.get('PlaceObjectID'), data.get('HallID'), err
                )
            )

    def _create_session(self, data, event, hall):
        """Create ticket session from data"""

        timestamp = self._parse_datetime(data.get('DateTime', None))
        show_timestamp = correct_night_session(timestamp) if timestamp is not None else None

        session, created = m.RamblerSession.objects.update_or_create(
            id=data.get('SessionID'), defaults=dict(
                event=event,
                hall=hall,
                city_id=data.get('CityID'),
                creation_class_type=data.get('CreationClassType', ''),
                place_class_type=data.get('PlaceClassType', ''),
                place_id=data.get('PlaceObjectID'),
                datetime=timestamp,
                show_datetime=show_timestamp,
                format=data.get('Format', ''),
                is_sale_available=data.get('IsSaleAvailable', False),
                is_reservation_available=data.get('IsReservationAvailable', False),
                is_without_seats=data.get('IsWithoutSeats', False),
                min_price=data.get('MinPrice') or None,
                max_price=data.get('MaxPrice') or None,
                hall_name=data.get('HallName', ''),
                fee_type=data.get('FeeType', ''),
                fee_value=data.get('FeeValue', ''),
            )
        )
        if created:
            log.debug('Add new session from Rambler.Kassa: {}'.format(session))

        return session

    def _clean_sessions(self, updated_sessions):
        """Clean invalid sessions"""

        log.debug('Deleting invalid sessions')
        invalid_sessions = m.RamblerSession.objects.exclude(id__in=updated_sessions)
        count = invalid_sessions.count()
        if count:
            invalid_sessions.delete()
            log.info('{} invalid sessions deleted'.format(count))

    def _parse_datetime(self, value):
        """Parse datetime string to DateTime object"""

        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            return None

    def _fill_date_start(self):
        """Заполнить поле «дата начала» у событий"""

        for re in m.RamblerEvent.objects.filter(date_start__isnull=True):
            try:
                rs = re.sessions.earliest()
                re.date_start = rs.datetime
                re.save(update_fields=['date_start'])
            except ObjectDoesNotExist:
                pass


class RamblerTicketCreator(TicketCreator):
    HALL_MODEL = m.RamblerHall
    EVENT_MODEL = m.RamblerEvent
    SOURCE = m.EventGuide.SOURCE_RAMBLER

    def parse_periods(self):
        """Return periods for ticket sessions"""

        sessions = self._ticket_sessions.order_by('hall', 'min_price', 'max_price', 'format', 'show_datetime')

        PeriodInfo = namedtuple('PeriodInfo', 'hall_id date times min_price max_price is_3d')

        for key, group in groupby(sessions, lambda s: (s.hall_id, s.min_price, s.max_price, '3D' in s.format)):
            hall_id, min_price, max_price, is_3d = key
            for date, items in groupby(group, lambda s: s.show_datetime.date()):
                times = list(i.show_datetime.time() for i in items)
                yield PeriodInfo(hall_id, date, times, min_price, max_price, is_3d)

    def create_period(self, event_guide, period_info):
        """Create single period"""

        period, created = m.Period.objects.get_or_create(
            event_guide=event_guide,
            start_date=period_info.date,
            end_date=period_info.date,
            is_3d=period_info.is_3d,
            defaults=dict(
                price=self._parse_price(period_info.min_price, period_info.max_price),
            ))
        if created:
            log.debug('Add new period: {}'.format(period.id))

        return period

    def create_sessions(self, period, period_info):
        """Create sessions for period by times"""

        for time in period_info.times:
            session, created = m.Sessions.objects.get_or_create(
                period=period, time=time, price=self._parse_price(period_info.min_price, period_info.max_price),
            )
            if created:
                log.debug('Add new session: {}'.format(session.id))

    def _parse_price(self, min_price, max_price):
        """Return human readable text for price"""

        if not min_price and not max_price:
            return ''
        elif min_price == max_price:
            return 'от {} руб.'.format(min_price)
        else:
            return '{}--{} руб.'.format(min_price, max_price)

    def _parse_duration(self, text):
        """
        Return datetime.time from text time representation

        >>> self._parse_duration('150 мин')
        >>> datetime.time(2, 30)
        >>> self._parse_duration('asdf')
        >>>
        """
        try:
            value = int(re.search(r'(\d+)', text).group())
            value = datetime.time(*divmod(value, 60))
        except (AttributeError, TypeError):
            return None
        else:
            return value
