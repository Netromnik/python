# -*- coding: utf-8 -*-

import re
import copy
import json
import logging

from django.conf import settings
from django.db.models import Model
from django.contrib.contenttypes.models import ContentType

from irk.utils.decorators import deprecated
from irk.utils.grabber import proxy_requests


logger = logging.getLogger(__name__)

EMPTY_OBJECT = object()


class ElasticSearchQuerySet(object):

    def __init__(self, model_or_iterable, query_params=None):
        if query_params is None:
            query_params = {}

        if isinstance(model_or_iterable, (list, tuple)):
            self.models = model_or_iterable
        else:
            self.models = (model_or_iterable, )
        self.query_params = query_params
        self.request_type = 'GET'

        self._result_cache = None
        self._meta = None

    def __len__(self):
        return self.count()

    def count(self):
        if self._meta is None:
            url, params = self._get_url('_count')
            if self.request_type == 'GET':
                response = proxy_requests.get(url, params=params, proxies=False).json()
            else:
                query_params = self.query_params.copy()
                # Исключаем ключи, не подходящие для _count запросов
                for key in ('size', 'sort', 'min_score', 'from'):
                    query_params.pop(key, None)
                response = proxy_requests.post(url, data=json.dumps(query_params), proxies=False).json()

            return response['count']

        try:
            return self.meta['hits']['total']
        except (KeyError, ):
            return 0

    def __nonzero__(self):
        if self._result_cache is None:
            self._get_data()

        return bool(self._result_cache)

    def __iter__(self):
        if self._result_cache is None:
            self._get_data()

        return iter(self._result_cache)

    def __getitem__(self, k):

        if isinstance(k, slice):
            start = int(k.start) if k.start is not None else 0
            stop = int(k.stop) if k.stop is not None else None

            kwargs = {
                'from': start,
            }
            if stop:
                kwargs['size'] = stop - start

            return self._clone(**kwargs)

        return list(self._clone(**{
            'from': k,
            'size': 1,
        }))[0]

    @property
    def meta(self):
        if self._meta is None:
            self._get_data()

        return self._meta

    def _get_data(self, direct=False):
        if self.request_type == 'GET':
            url, params = self._get_url()
            response = proxy_requests.get(url, params=params, proxies=False).json()
        else:
            url = self._get_base_url()
            response = proxy_requests.post(url, data=json.dumps(self.query_params), proxies=False).json()

        if direct:
            return response

        try:
            self._meta = {
                'took': response['took'],
                '_shards': response['_shards'],
                'hits': {
                    'total': response['hits']['total'],
                    'max_score': response['hits']['max_score'],
                },
            }
        except KeyError:
            # Поиск не дал результатов
            self._result_cache = ()
            return

        hits = response['hits']['hits']

        fields = self.query_params.get('fields')
        if not fields:
            object_ids = [int(x['_id']) for x in hits]
            object_types = list(set(x['_type'] for x in hits))

            # Все документы одного типа
            if len(object_types) == 1:
                app_label, model_name = object_types[0].split('_')
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
                objects = ct.get_all_objects_for_this_type(id__in=object_ids)
            else:
                objects = []
                for type_ in object_types:
                    app_label, model_name = type_.split('_')
                    ct = ContentType.objects.get(app_label=app_label, model=model_name)
                    objects += ct.get_all_objects_for_this_type(id__in=[x['_id'] for x in hits if x['_type'] == type_])

            self._result_cache = sorted(objects, key=lambda x: object_ids.index(x.id))

        else:
            try:
                id_field_idx = fields.index('id')
            except ValueError:
                id_field_idx = None

            if id_field_idx is not None:
                fields = list(fields)
                fields.remove('id')

            self._result_cache = []
            for obj in hits:
                dump = [obj['fields'][key] for key in fields]
                if id_field_idx is not None:
                    dump.insert(id_field_idx, int(obj['_id']))

                self._result_cache.append(dump)
                # TODO: похоже строка осталась от кривого мерджа, т.к. выше делается тоже самое
                self._result_cache.append([obj['fields'][key] for key in fields])

    def _get_url(self, postfix='_search'):
        url = self._get_base_url(postfix)

        params = self.query_params.copy()
        params.update({
            'default_operator': 'AND',
        })

        fields = self.query_params.get('fields')
        if fields is None:
            fields = ['id', ]
        params['fields'] = ','.join(fields)

        query = params.get('q', [])
        if query is None:
            query = []

        if isinstance(query, (str, unicode)):
            query = re.escape(query)
            query = [query, ]

        if query:
            params['q'] = ' AND '.join(query)

        return url, params

    def _get_base_url(self, postfix='_search'):
        return 'http://{host}:{port}/search/{types}/{postfix}'.format(**{
            'host': settings.ELASTICSEARCH_ADDRESS['HOST'],
            'port': settings.ELASTICSEARCH_ADDRESS['PORT'],
            'types': ','.join(['{0}_{1}'.format(x._meta.app_label, x._meta.object_name.lower()) for x in self.models]),
            'postfix': postfix,
        })

    @deprecated  # Используется :method:`self.filter`
    def query(self, query):
        return self._clone(**query)

    def all(self):
        return self._clone()

    def distinct(self):
        return self._clone()

    def filter(self, *args, **kwargs):
        # TODO: support for Q objects

        query = self.query_params.get('q', [])
        for field, value in kwargs.items():
            field = field.replace('__exact', '')

            if isinstance(value, Model):
                value = value.pk

            if isinstance(value, (str, unicode)) and self.request_type == 'GET':
                # Экранируем спецсимволы в параметрах GET запросов
                value = value.replace(':', '\\:')

            elif isinstance(value, (list, tuple)):
                value = u'({0})'.format(u' OR '.join(str(x) for x in value))

            query.append(u'{0}:{1}'.format(field, value))

        return self._clone(q=query)

    def order_by(self, *args):
        """Сортировка результатов

        Реализован интерфейс, аналогичный `django.db.QuerySet`, например
            Model.search.filter(title='foo').order_by('-id', 'created')
        """

        params = []
        for field in args:
            field_name = field.lstrip('-')

            # В ElasticSearch поле называется по другому
            if field_name == 'id':
                field_name = '_id'

            params.append('{}:{}'.format(field_name, 'desc' if field[0] == '-' else 'asc'))

        return self._clone(sort=','.join(params))

    def none(self):
        qs = self._clone()
        qs.query_params = {}

        return qs

    def values_list(self, *fields, **kwargs):
        # TODO: сделать поддержку параметра `flat=True`
        # После реализации переделать поиск Афиши
        return self._clone(fields=fields)

    def raw(self, data, direct=False):
        """Прямой POST запрос к ElasticSearch

        Если `direct` равен True, сразу же возвращается ответ от ElasticSearch
        """

        qs = self._clone(**data)
        qs.request_type = 'POST'

        if direct:
            return qs._get_data(direct=True)

        return qs

    def _clone(self, **kwargs):
        instance = self.__class__(copy.copy(self.models), self.query_params.copy())
        instance.__dict__.update(self.__dict__.copy())

        instance._result_cache = None
        instance._meta = None
        instance.query_params.update(kwargs.copy())

        return instance
