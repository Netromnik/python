# -*- coding: utf-8 -*-
"""
Интерфейс для получения данных из Яндекс.Метрики

С результатами работать сложно, потому что тяжело найти в них нужную строку.
Из-за того, что называния группировок не хранятся в самих данных, приходится
писать сложные итераторы.

В этом файле есть пара классов для облегчения задачи поиска. Вот, например,
как можно получить сумму просмотров с мобильных устройств

```
    # выберем строки
    rows = filter(lambda row: row.dimension('deviceCategory')['id'] in device, response['data'])

    # просуммируем
    total_views = reduce(lambda views, row: views + row.metric('pageviews'), rows, 0)
```

Тут методы `.dimension` и `.metric` сильно облегчают работу.

"""
from __future__ import absolute_import, unicode_literals

from django.conf import settings

from irk.utils.grabber import proxy_requests


class YandexMetrikaError(Exception):
    pass


class YandexMetrikaGrabber(object):
    base_url = 'https://api-metrika.yandex.ru/stat/v1/data'

    def __init__(self, kind=''):
        if not settings.YANDEX_METRIKA_API_COUNTER_ID:
            raise ValueError('YANDEX_METRIKA_API_COUNTER_ID is not set in settings.py')
        if not settings.YANDEX_METRIKA_API_OAUTH_TOKEN:
            raise ValueError('YANDEX_METRIKA_API_OAUTH_TOKEN is not set in settings.py')

        self.params = {}
        self.kind = kind
        self.set_param(id=settings.YANDEX_METRIKA_API_COUNTER_ID)
        self.headers = {'Authorization': 'OAuth {}'.format(settings.YANDEX_METRIKA_API_OAUTH_TOKEN)}

    def set_param(self, **kwargs):
        for k, v in kwargs.items():
            self.params[k] = v

    def del_param(self, alias):
        del self.params[alias]

    def run(self, extra_params=None, kind=''):
        params = self.params.copy()
        if extra_params:
            # extra params не меняет внутреннее состояние объекта.
            # это чтобы можно было много запросов на одну дату запускать
            params.update(extra_params)

        url = '{}/{}'.format(self.base_url, kind or self.kind)
        data = proxy_requests.get(url, params=params, headers=self.headers).json()
        if 'code' in data:
            msg = u'{} {}'.format(data.get('code', ''), data.get('message', ''))
            raise YandexMetrikaError(msg.encode('utf-8'))

        return data


class MetrikaResult(dict):
    """
    Обертка вокруг ответа Метрики для удобного доступа к названиям группировок
    """
    def __init__(self, *args, **kwargs):
        super(MetrikaResult, self).__init__(*args, **kwargs)
        # заменим строки с данными на инстансы MetrikaResultRow
        if self['data']:
            self['data'] = [MetrikaResultRow(row, result=self) for row in self['data']]


class MetrikaResultRow(dict):
    def __init__(self, *args, **kwargs):
        # сохраним ссылку на весь результат ответа метрики
        if 'result' in kwargs:
            self.result = kwargs['result']
            del kwargs['result']

        super(MetrikaResultRow, self).__init__(*args, **kwargs)

    def dimension(self, key):
        """
        Возвращает dimension из этой строки, зная его название, а не индекс. Например:

            > response['data'][0].dimension('ym:pv:deviceCategory')
            {'name': 'тв', 'id': 'tv'}

        Можно передавать только часть названия
        """
        for idx, name in enumerate(self.result['query']['dimensions']):
            if key.lower() in name.lower():
                return self['dimensions'][idx]

    def metric(self, key):
        """
        Возвращает metric из этой строки по названию метрики

            > response['data'][0].metric('pageviews')
            8862.0
        """
        for idx, name in enumerate(self.result['query']['metrics']):
            if key.lower() in name.lower():
                return self['metrics'][idx]
