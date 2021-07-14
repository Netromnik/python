# -*- coding: utf-8 -*-

import datetime
import hashlib
import logging

import requests
from lxml import etree

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from irk.afisha import settings as app_settings
from irk.afisha.models import Event, Guide, KassyBuilding, KassyEvent, KassyHall, KassyRollerman, KassySession
from irk.afisha.tickets.helpers import correct_night_session
from irk.utils.helpers import datetime_to_unixtime, float_or_none, int_or_none, unixtime_to_datetime


logger = logging.getLogger(__name__)


def unescape(text):
    """Убирает экранирование Html"""

    return text.replace(u'&quot;', u'"')


class KassyApi(object):
    """Класс предоставляет низкоуровневый интерфейс для работы с api kassy.ru"""

    def __init__(self, db, agent_id, secret):
        """
        :param str db: подразделение, которому адресованы запросы
        :param str agent_id: идентификатор агента
        :param str secret: секретный ключ агента
        """

        self._db = db
        self._agent_id = agent_id
        self._secret = secret

        self._api_url = 'https://api.kassy.ru/v1/'

    def post(self, module_name, filters=None, response_format='json'):
        """
        Отправить запрос к модулю

        :param str module_name: модуль или функция api
        :param dict filters: словарь фильтров. Default: None
        :param str response_format: формат ответа. Default: json
        """

        xml = self._make_xml(module_name, filters, response_format)
        request_data = {
            'xml': xml,
            'sign': self._generate_sign(xml)
        }

        response = requests.post(self._api_url, data=request_data, verify=False)

        # TODO: обработка ошибок

        if response_format == 'json':
            response_data = response.json()
        else:
            response_data = response.content

        return response_data

    def _make_xml(self, module_name, filters, response_format):
        """
        Создать xml данные для запроса

        :param str module_name: модуль или функция api
        :param dict filters: словарь фильтров. Default: None
        :param str response_format: формат ответа. Default: json
        :rtype: str
        """

        xml = etree.Element('request', db=self._db, module=module_name, format=response_format)

        if filters:
            # для создания элемента параметры нужно привести к строковому типу
            filters = {key: unicode(value) for key, value in filters.items()}
            etree.SubElement(xml, 'filter', **filters)

        etree.SubElement(xml, 'auth', id=self._agent_id)

        return etree.tostring(xml, encoding='utf-8', xml_declaration=True)

    def _generate_sign(self, data):
        """
        Сгенерировать подпись пакета

        :param str data: данные
        :rtype: str
        """

        md5 = hashlib.md5()
        md5.update(data)
        md5.update(self._secret)

        return md5.hexdigest()


class KassyGrabber(object):
    """
    Граббер событий из системы kassy.ru

    Заполняет модели KassyEvent и KassySession
    """

    def __init__(self):
        self._api = KassyApi(app_settings.KASSY_DB, app_settings.KASSY_AGENT_ID, app_settings.KASSY_SECRET)

    def run(self):
        """Запустить граббер"""

        start_date = datetime.date.today()
        # Запрашиваются события на год вперед
        end_date = start_date + datetime.timedelta(days=365)

        filters = {
            'date_from': datetime_to_unixtime(start_date),
            'date_to': datetime_to_unixtime(end_date),
        }

        self._grab_rollermans()

        data = self._api.post('page_event_list', filters).get('data', {})
        self._parse_buildings(data.get('buildings', []))
        self._parse_halls(data.get('halls', []))
        self._parse_events(data.get('shows', []))
        self._parse_sessions(data.get('events', []))

        self._fill_date_start()

        logger.info(u'События с kassy.ru успешно загружены.')

    def _grab_rollermans(self):
        """Получить организаторов."""

        rollermans_data = self._api.post('table_rollerman').get('data', [])

        for rollerman_data in rollermans_data:
            kassy_rollerman, created = KassyRollerman.objects.update_or_create(
                id=rollerman_data.get('id'), defaults={
                    'name': unescape(rollerman_data.get('name', '') or ''),
                    'email': rollerman_data.get('email', ''),
                    'address': unescape(rollerman_data.get('address', '') or ''),
                    'phone': rollerman_data.get('phone', ''),
                    'inn': rollerman_data.get('inn', ''),
                    'okpo': rollerman_data.get('okpo', ''),
                    'state': bool(rollerman_data.get('state', False)),
                }
            )

            if created:
                logger.debug(u'Add new rollerman from kassy.ru: {}'.format(kassy_rollerman.id))

    def _parse_buildings(self, buildings_data):
        """Получить учреждения."""

        for building_data in buildings_data:
            building, created = KassyBuilding.objects.update_or_create(
                id=building_data.get('id'), defaults={
                    'type_id': int_or_none(building_data.get('type_id')),
                    'region_id': int_or_none(building_data.get('region_id')),
                    'title': unescape(building_data.get('title', '') or ''),
                    'descr': unescape(building_data.get('descr', '') or ''),
                    'address': unescape(building_data.get('address', '') or ''),
                    'phone': building_data.get('phone', '') or '',
                    'url': building_data.get('url', ''),
                    'workhrs': building_data.get('workhrs', ''),
                    'hall_count': int_or_none(building_data.get('hall_count')),
                    'marginprc': int_or_none(building_data.get('marginprc')),
                    'geo_lat': float_or_none(building_data.get('geo_lat')),
                    'geo_lng': float_or_none(building_data.get('geo_lng')),
                    'is_sale': bool(building_data.get('is_sale', False)),
                    'is_reserv': bool(building_data.get('is_reserv', False)),
                    'is_pos': bool(building_data.get('is_pos', False)),
                    'state': bool(building_data.get('state', False)),
                }
            )

            if created:
                logger.debug(u'Add new building from kassy.ru: {}'.format(building))

    def _parse_halls(self, halls_data):
        """Получить залы"""

        for hall_data in halls_data:

            # Бывает, что kassy шлет данные по залу не отправляя при этом данные по заведению. Их нужно пропускать.
            # Это связано с тем, что свои акции они отдают в виде события https://irk.kassy.ru/event/2943/
            building_id = int_or_none(hall_data.get('building_id'))
            if building_id and KassyBuilding.objects.filter(pk=building_id).exists():
                hall, created = KassyHall.objects.update_or_create(
                    id=hall_data.get('id'), defaults={
                        'building_id': building_id,
                        'title': unescape(hall_data.get('title', '') or ''),
                        'descr': unescape(hall_data.get('descr', '') or ''),
                        'update': unixtime_to_datetime(hall_data.get('update', '')),
                        'is_navigated': bool(hall_data.get('is_navigated', False)),
                        'width': int_or_none(hall_data.get('width')),
                        'height': int_or_none(hall_data.get('height')),
                        'hidden': bool(hall_data.get('hidden', False)),
                        'state': bool(hall_data.get('state', False)),
                    }
                )

                if created:
                    logger.debug(u'Add new hall from kassy.ru: {}'.format(hall))

    def _parse_events(self, events_data):
        """
        Получить события.
        В системе kassy.ru это зрелища (shows).
        """

        for event_data in events_data:
            event, created = KassyEvent.objects.update_or_create(
                id=event_data.get('id'), defaults={
                    'type_id': int_or_none(event_data.get('type_id')),
                    'kassy_rollerman_id': int_or_none(event_data.get('rollerman_id')),
                    'title': unescape(event_data.get('title', '')),
                    'marginprc': int_or_none(event_data.get('marginprc')),
                    'duration': int_or_none(event_data.get('duration')),
                    'age_restriction': event_data.get('age_restriction', ''),
                    'rating': int_or_none(event_data.get('rating')),
                    'announce': unescape(event_data.get('announce', '') or ''),
                    'image': self._get_image_url(event_data.get('image', '')),
                    'is_sale': bool(event_data.get('is_sale', False)),
                    'is_reserv': bool(event_data.get('is_reserv', False)),
                    'state': bool(event_data.get('state', False)),
                }
            )

            if created:
                logger.debug(u'Add new event from kassy.ru: {}'.format(event))

    def _parse_sessions(self, sessions_data):
        """
        Получить сеансы.
        В системе kassy.ru это события (events).
        """

        for session_data in sessions_data:
            # kassy добавляет в API собственые акции https://irk.kassy.ru/event/2943/ которые не нужны на сайте
            # из-за этого нужны дополнительные проверки
            event_id = int_or_none(session_data.get('show_id'))
            hall_id = int_or_none(session_data.get('hall_id'))
            if event_id and hall_id and KassyHall.objects.filter(pk=hall_id).exists() and \
                KassyEvent.objects.filter(pk=event_id).exists():

                timestamp = unixtime_to_datetime(session_data.get('date', ''))
                show_timestamp = correct_night_session(timestamp) if timestamp is not None else None

                session, created = KassySession.objects.update_or_create(
                    id=session_data.get('id'), defaults={
                        'event_id': event_id,
                        'hall_id': hall_id,
                        'datetime': timestamp,
                        'price_min': int_or_none(session_data.get('price_min')),
                        'price_max': int_or_none(session_data.get('price_max')),
                        'vacancies': int_or_none(session_data.get('vacancies')),
                        'is_gst': bool(session_data.get('is_gst', False)),
                        'is_prm': bool(session_data.get('is_prm', False)),
                        'is_recommend': bool(session_data.get('is_recommend', False)),
                        'sale_state': int_or_none(session_data.get('sale_state')) or KassySession.SALE_STATE_END,
                        'state': bool(session_data.get('state', False)),
                        'show_datetime': show_timestamp,
                    }
                )

                if created:
                    logger.debug(u'Add new session from kassy.ru: {}'.format(session))

    def _get_image_url(self, image):
        """Получить полный адрес изображения"""

        if not image:
            return ''

        return u'http://{}.kassy.ru/media/{}'.format(app_settings.KASSY_DB, image)

    def _fill_date_start(self):
        """Заполнить поле «дата начала» у событий"""

        for ke in KassyEvent.objects.filter(date_start__isnull=True):
            try:
                ks = ke.sessions.earliest()
                ke.date_start = ks.datetime
                ke.save()
            except ObjectDoesNotExist:
                pass
