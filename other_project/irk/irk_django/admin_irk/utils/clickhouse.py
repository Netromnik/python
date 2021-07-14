# coding=utf-8
from __future__ import unicode_literals

import requests
import logging
import csv

from django.conf import settings

CLICKHOUSE_URL = settings.CLICKHOUSE_URL
session = requests.Session()  # сессия держит пул открытых сокетов
logger = logging.getLogger(__name__)


csv.register_dialect('clickhouse', escapechar=b'\\', doublequote=0, quotechar=b'\'',
                     delimiter=b'\t', quoting=csv.QUOTE_NONE, lineterminator=b'\n')


def make_client():
    global session
    return Client(session)


def execute(sql, params=None):
    """
    Выполняет запрос к кликхаусу методом GET по HTTP-интерфейсу
    """
    http_response = session.get(CLICKHOUSE_URL, params={'query': sql})

    if http_response.status_code != 200:
        raise ClickhouseException(http_response.text)

    return Response(http_response)


class Client(object):
    """
    Вспомогательный класс для вставки и селекта из кликхауса по HTTP интерфейсу
    """
    def __init__(self, session):
        self.session = session

    def insert_bulk(self, table, keys, rows):
        """
        Массовая вставка строк из готовой переменной `rows` в формате TSV
        """
        query = 'INSERT INTO {table}({keys}) FORMAT TabSeparated'.format(
            table=table,
            keys=self._keys(keys)
        )

        logger.debug('bulk insertion')
        logger.debug('data length: %s', len(rows))

        resp = self.session.post(CLICKHOUSE_URL, params={'query': query}, data=rows)

        if resp.status_code != 200:
            msg = 'HTTP {}: {}'.format(resp.status_code, resp.text)
            raise ValueError(msg)

        return resp

    def _keys(self, keys):
        _keys = [k.replace(',', '') for k in keys]  # экранируем запятую
        return ','.join(_keys)


class Response(object):
    def __init__(self, http_response):
        json = http_response.json()
        self.meta = json['meta']
        self.data = json['data']
        self.rows = json['rows']
        self.statistics = json['statistics']

        self.status_code = http_response.status_code
        self.text = http_response.text


class ClickhouseException(Exception):
    pass


def make_tsv(values):
    return '\t'.join((str(v).replace('\t', '-') for v in values))
