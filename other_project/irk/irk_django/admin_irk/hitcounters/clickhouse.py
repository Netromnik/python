# coding=utf-8
"""
Отчеты кликхауса по поводу просмотров страниц (не по поводу рекламы)
Пока не используется, эксперимент
"""
import datetime
import logging

import requests
from django.conf import settings

from irk.hitcounters.helpers import get_hitcounter_info


CLICKHOUSE_URL = settings.CLICKHOUSE_URL
s = requests.Session()  # сессия держит пул открытых сокетов
logger = logging.getLogger(__name__)


def save_page_view(request, obj):

    """
        CREATE TABLE hits2 (
            ObjectClass String,
            ObjectId UInt32,
            Date Date,
            DateTime DateTime,
            URL String,
            IP String,
            Referer String,
            UserAgent String,
            IsMobile UInt8,
            IsTablet UInt8,
            IsPc UInt8,
            IsBot UInt8,
            BrowserFamily String,
            BrowserVersion String,
            OS String,
            OsVersion String,
            DeviceFamily String,
            SessionId String
        )
        ENGINE = MergeTree()
        PARTITION BY toYYYYMM(Date)
        ORDER BY (ObjectId, ObjectClass)
    """

    info = get_hitcounter_info(obj)

    now = datetime.datetime.now()

    if not info:
        logger.info('Object %s %d is not countable', obj.__class__, obj.id)
        logger.info('You need to add it to the COUNTABLE_OBJECTS')
        return

    data = {
        'ObjectClass': info['obj_type'],
        'ObjectId': obj.id,
        'Date': '{:%Y-%m-%d}'.format(now),
        'DateTime': '{:%Y-%m-%d %H:%M:%S}'.format(now),
        'URL': request.build_absolute_uri(),
        'Referer': request.META.get('HTTP_REFERER', ''),
        'IP': request.META.get('REMOTE_ADDR', ''),
        'UserAgent': request.META.get('HTTP_USER_AGENT', ''),
        'IsMobile': int(request.user_agent.is_mobile),
        'IsTablet': int(request.user_agent.is_tablet),
        'IsPc': int(request.user_agent.is_pc),
        'IsBot': int(request.user_agent.is_bot),
        'BrowserFamily': request.user_agent.browser.family,
        'BrowserVersion': request.user_agent.browser.version_string,
        'OS': request.user_agent.os.family,
        'OsVersion': request.user_agent.os.version_string,
        'DeviceFamily': request.user_agent.device.family,
        'SessionId': request.session.session_key or '',
    }

    # print(request.META)

    keys, values = data.keys(), data.values()

    for k, v in data.items():
        logger.debug('{:16}: {}'.format(k, v))

    query = 'INSERT INTO hits2({keys}) FORMAT TabSeparated'.format(keys=','.join(keys))
    data = '\t'.join((str(v).replace('\t', '-') for v in values))

    try:
        resp = s.post(CLICKHOUSE_URL, data, params={'query': query}, timeout=0.0000000001)
        logger.info('Response: [%s] %s', resp.status_code, resp.text)
    except requests.exceptions.ReadTimeout:
        logger.debug('Timeout')
    except requests.exceptions.ConnectionError:
        # пока у нас тестовый режим, принимающий порт может быть закрыт
        # ответим спокойно сообщением - чтобы не забивать лог трейсом ошибки
        logger.debug('ClickHouse backend port is closed')


def get_page_hits(obj_class, obj_id):

    query = \
        "SELECT COUNT(), uniq(SessionId) FROM hits2 " \
        "WHERE ObjectClass=%(obj_class)s AND ObjectId=%(obj_id)s AND IsBot=0"
    params = {'obj_class': obj_class, 'obj_id': obj_id}
