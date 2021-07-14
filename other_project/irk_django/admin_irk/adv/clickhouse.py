# coding=utf-8
"""
Функции для работы с аналитическим бекендом - кликхаусом

Структура таблицы `events`:

    CREATE TABLE default.events
    (
        `EventType` UInt8,
        `EventDate` Date,
        `EventDateTime` DateTime,
        `BannerId` UInt32,
        `FileId` UInt32,
        `PlaceId` UInt32,
        `ClientIP` IPv4,
        `URL` String,
        `Referer` String,
        `UserAgent` String,
        `IsMobile` UInt8,
        `IsTablet` UInt8,
        `IsPc` UInt8,
        `IsBot` UInt8,
        `BrowserFamily` String,
        `BrowserVersion` String,
        `OS` String,
        `OsVersion` String,
        `DeviceFamily` String,
        `SessionId` String
    )
    ENGINE = MergeTree()
    PARTITION BY (toYYYYMM(EventDate), IsBot)
    ORDER BY EventDateTime
    SETTINGS index_granularity = 8192

"""
import copy
import random
import datetime
import logging
from collections import defaultdict
from StringIO import StringIO
import csv

from redis import TimeoutError

from irk.utils.clickhouse import execute, make_client
from irk.utils.db.kv import get_redis
from irk.utils.sql import select

logger = logging.getLogger(__name__)
# таймаут, чтобы если редис подвис, не зависал весь сайт
# обычно вставка занимает 1 мс, ставим лимит 100
redis = get_redis(socket_timeout=0.1)


def place_report(date_start=None, date_end=None):
    """
    Статистика баннерных мест: показы, показы в зоне видимости
    """
    query = select('PlaceId, EventType, count() AS cnt').from_('events') \
        .where('IsBot = 0') \
        .group_by('PlaceId, EventType') \
        .order_by('cnt DESC') \
        .format('JSON')

    if date_start:
        query = query.where("EventDate >= '{:%Y-%m-%d}'".format(date_start))
    if date_end:
        query = query.where("EventDate <= '{:%Y-%m-%d}'".format(date_end))

    sql = query.sql()
    logger.debug('SQL: %s', sql)

    resp = execute(sql)
    logger.debug('Response: [%s] %s rows', resp.status_code, resp.rows)
    logger.debug('Response: %s', resp.statistics)

    rows = resp.data

    result = defaultdict(dict)
    for item in rows:
        if item['EventType'] == 1:
            key = 'Loads'
        elif item['EventType'] == 2:
            key = 'Impressions'
        result[item['PlaceId']][key] = item['cnt']

        result[item['PlaceId']]['EventType{}Count'.format(item['EventType'])] = item['cnt']
        result[item['PlaceId']]['PlaceId'] = item['PlaceId']

    result = list(result.values())
    return result


def place_report_add_titles(data):
    """
    Добавить названия баннерных позиций по PlaceId в отчет выше
    """
    from irk.adv.models import Place

    titles = {}
    for id, title in Place.objects.all().values_list('id', 'name'):
        titles[id] = title

    data2 = []
    for row in data:
        row_copy = copy.copy(row)
        if row['PlaceId'] in titles:
            row_copy['PlaceTitle'] = titles[row['PlaceId']]
        data2.append(row_copy)

    return data2


def save_place_view(place_id, request):
    """
    Логирует показ баннерного места
    """
    stream = EventStream(redis)
    stream.push_place_view(place_id, request)


def move_to_clickhouse(chunk_size=50000):
    uploader = ClickhouseUploader()
    uploader.upload(chunk_size)


class EventStream(object):
    """
    Поток событий

    Сразу загружать аналитические события в кликхаус нельзя. Он не поддерживает
    такое количество вставок, которое мы генерируем. Поэтому мы сначала добавляем
    все события в единый поток, очередь. А потом отдельный скрипт забирает из
    потока сразу N событий и вставляет их в кликхаус батчем.

    Сейчас очередь реализована через Redis. Но можно в будущем заменить его
    на Kafka.

    Данные сохраняются в редис простым добавлением в словарь с ключом `adv:events:v1`
    В словарь добавляются закодированные в TSV строки, которые потом можно сразу
    импортировать.

    Версия тут нужна, потому что во всех строках, сохраняемых в редис, один
    набор колонок. Если набор колонок меняется, он автоматически должен попадать
    в другой ключ, в другую очередь.
    """

    TYPE_PLACE_VIEW = 1
    TYPE_BANNER_VIEW = 2
    TYPE_BANNER_IMPRESSION = 3

    # два параметра ниже меняются вместе
    CLICKHOUSE_KEYS_VERSION = 'v2'
    CLICKHOUSE_KEYS = (
        'EventDate',
        'EventDateTime',
        'EventType',
        'PlaceId',
        'ClientIP',
        'URL',
        'Referer',
        'UserAgent',
        'IsMobile',
        'IsTablet',
        'IsPc',
        'IsBot',
        'BrowserFamily',
        'BrowserVersion',
        'OS',
        'OsVersion',
        'DeviceFamily',
        'SessionId',
    )

    QUEUE_MAX_SIZE = 50*1000*1000
    QUEUE_LIMITER_FREQ = 100

    def __init__(self, redis=None):
        self.redis = redis

    def keys(self):
        return self.CLICKHOUSE_KEYS

    def version(self):
        return self.CLICKHOUSE_KEYS_VERSION

    def push_place_view(self, place_id, request):
        """
        Показ баннерного места
        """
        # данные события
        event_data = self._place_view_data(place_id, request)

        # закодируем в tsv с фиксированным набором колонок
        tsv, version = self._encode(event_data)

        # добавим в очередь
        try:
            self.redis.rpush('adv:events:' + version, tsv)
        except TimeoutError:
            logger.warning('Redis rpush > 100 ms, skipping place view logging')

        self._limit_queue_size('adv:events:' + version)

    def push_banner_view(self, banner_id, file_id, request):
        pass

    def push_banner_impression(self):
        pass

    def _place_view_data(self, place_id, request):
        """
        Создает словарь с данными о просмотре баннерного места
        """
        now = datetime.datetime.now()

        data = {
            'EventDate': '{:%Y-%m-%d}'.format(now),
            'EventDateTime': '{:%Y-%m-%d %H:%M:%S}'.format(now),
            'EventType': self.TYPE_PLACE_VIEW,
            'PlaceId': int(place_id),
            'ClientIP': request.META.get('REMOTE_ADDR', ''),
            'URL': request.build_absolute_uri(),
            'Referer': request.META.get('HTTP_REFERER', ''),
            'UserAgent': request.META.get('HTTP_USER_AGENT', ''),
            'IsMobile': 0,
            'IsTablet': 0,
            'IsPc': 0,
            'IsBot': 0,
            'BrowserFamily': '',
            'BrowserVersion': '',
            'OS': '',
            'OsVersion': '',
            'DeviceFamily': '',
            'SessionId': '',
        }

        if hasattr(request, 'user_agent'):
            data['IsMobile'] = int(request.user_agent.is_mobile)
            data['IsTablet'] = int(request.user_agent.is_tablet)
            data['IsPc'] = int(request.user_agent.is_pc)
            data['IsBot'] = int(request.user_agent.is_bot)
            data['BrowserFamily'] = request.user_agent.browser.family
            data['BrowserVersion'] = request.user_agent.browser.version_string
            data['OS'] = request.user_agent.os.family
            data['OsVersion'] = request.user_agent.os.version_string
            data['DeviceFamily'] = request.user_agent.device.family

        if hasattr(request, 'session'):
            data['SessionId'] = request.session.session_key

        for k, v in data.items():
            logger.debug('{:16}: {}'.format(k, v))

        return data

    def _encode(self, data):
        """
        Кодирует данные словаря `data` в tsv, используя порядок и ключи из KEYS

        Данные кодируются так, чтобы потом сразу импортировать их в кликхаус

        Если в `data` есть ключи, которых нет в `fieldnames`, выдаст ValueError
        Если в `data` не хватает каких-то значений, то ничего страшного
        """
        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=self.keys(), dialect='clickhouse')
        writer.writerow(data)

        return buffer.getvalue(), self.version()

    def _limit_queue_size(self, queue):
        """
        Функция-предохранитель, чтобы размер очереди не переполнился
        В редисе версии 3 нет возможности ограничить размер очереди
        Это нужно, например, если сломается скрипт, вычищающий очередь
        """
        if random.randint(0, self.QUEUE_LIMITER_FREQ) == 0:
            logger.debug('Starting queue limiter')

            # запускается раз в QUEUE_LIMITER_FREQ вставок
            if self.redis.llen(queue) > self.QUEUE_MAX_SIZE:
                self.redis.ltrim(queue, -self.QUEUE_MAX_SIZE, -1)
                logger.warning('QUEUE size is too large, check consumer script!')


class ClickhouseUploader(object):
    """Массово переносит данные из редиса в кликхаус"""

    def __init__(self, redis=None, house=None):
        self.default_chunk_size = 50000
        self.key = 'adv:events:v2'

        if redis:
            self.redis = redis
        else:
            self.redis = get_redis()  # без таймаута
        if house:
            self.house = house
        else:
            self.house = make_client()

    def upload(self, chunk_size=None):
        """
        Скачивает из редиса события кусками и загружает в кликхаус
        """
        chunk_size = chunk_size if chunk_size else self.default_chunk_size

        while True:
            logger.debug('loading chunk of %s rows', chunk_size)
            chunk = self.redis.lrange(self.key, 0, chunk_size-1)

            if not chunk:
                break

            if len(chunk) <= chunk_size * 0.2:
                # не обрабатывать слишком маленькие кусочки, чтобы не было race condition,
                # когда бекенд добавляет в редис все новые и новые записи, а мы все крутим
                # и крутим цикл
                logger.debug('remainder chunk is too small, skipping')
                break

            logger.debug('uploading %d rows', len(chunk))
            keys = EventStream().keys()
            data = b''.join(chunk)

            # отправим все строки в кликхаус
            result = self.house.insert_bulk('events', keys, data)
            logger.debug('result: HTTP %s %s', result.status_code, result.text)

            # удалим из начала столько, сколько обработали
            self.redis.ltrim(self.key, len(chunk), -1)
