# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import io
import json
import logging

from django.conf import settings
from django.contrib.gis.db import models

from irk.utils.grabber import proxy_requests

log = logging.getLogger(__name__)

FIELD_MAPPINGS = {
    models.CharField: {'type': 'string', 'analyzer': 'ru'},
    models.TextField: {'type': 'string', 'analyzer': 'ru'},
    models.ForeignKey: {'type': 'long'},
    models.DateTimeField: {
        'type': 'date', 'format': 'date_hour_minute_second || date_hour_minute_second_millis'
    },
    models.DateField: {'type': 'date', 'format': 'date'},
    models.IntegerField: {'type': 'long'},
    models.SlugField: {'type': 'string'},
    models.BooleanField: {'type': 'boolean'},
    models.FloatField: {'type': 'float'},
    models.PositiveIntegerField: {'type': 'long'},
    models.TimeField: {'type': 'date', 'format': 'hour_minute_second'},
    models.PointField: {'type': 'geo_point'},
}


class ElasticSearchControllerError(Exception):
    pass


class ElasticSearchControllerRequestError(ElasticSearchControllerError):
    pass


class ElasticSearchController(object):
    """Provide methods for control elasticsearch"""

    base_url = 'http://{host}:{port}'.format(
        host=settings.ELASTICSEARCH_ADDRESS['HOST'],
        port=settings.ELASTICSEARCH_ADDRESS['PORT'],
    )

    index_url = base_url + '/search'
    type_url = index_url + '/{0.index_name}_{0.type}'
    bulk_url = base_url + '/_bulk'

    def create_index(self):
        self.request(
            'PUT', self.index_url, data=json.dumps(settings.ELASTICSEARCH_INDEX_DEFAULT_SETTINGS)
        )

    def create_type(self, model_search):
        properties = self._get_properties(model_search)

        key = '{index}_{type}'.format(index=model_search.index_name, type=model_search.type)
        payload = {
            key: {
                '_source': {
                    'enabled': True,
                },
                '_all': {
                    'enabled': True,
                    'analyzer': 'ru',
                },
                'properties': properties,
            },
        }

        url = self.type_url.format(model_search) + '/_mapping'
        self.request('PUT', url, data=json.dumps(payload))

    def delete_index(self):
        self.request('DELETE', self.index_url)

    def delete_type(self, model_search):
        url = self.type_url.format(model_search)
        self.request('DELETE', url)

    def recreate_type(self, model_search):
        if self.type_exists(model_search):
            self.delete_type(model_search)

        self.create_type(model_search)

    def close_index(self):
        self.request('POST', '{}/_close'.format(self.index_url))

    def open_index(self):
        self.request('POST', '{}/_open'.format(self.index_url))

    def reload_settings(self):
        self.close_index()
        try:
            self.request(
                'PUT', '{}/_settings'.format(self.index_url),
                data=json.dumps(settings.ELASTICSEARCH_INDEX_DEFAULT_SETTINGS),
            )
            return True
        except ElasticSearchControllerRequestError:
            return False
        finally:
            self.open_index()

    def bulk_create(self, search, chunk_size):
        action_and_meta_data = json.dumps({
            'index': {
                '_index': 'search',
                '_type': '%s_%s' % (search.index_name, search.type),
                '_id': '%s',
            }
        })

        queryset = search.get_queryset()
        total = queryset.count()
        for start in range(0, total, chunk_size):
            payload = io.BytesIO()
            end = min(start + chunk_size, total)

            for obj in list(queryset[start:end]):
                if search.abstract:
                    search.update_search(obj)
                    continue

                data = search.serialize(obj.pk, obj)

                payload.write(action_and_meta_data % obj.pk)
                payload.write(b'\n')
                payload.write(data)
                payload.write(b'\n')

            self.request('POST', self.bulk_url, data=payload.getvalue())

    def index_exists(self):
        return self.request('HEAD', self.index_url).ok

    def type_exists(self, model_search):
        url = self.type_url.format(model_search)
        return self.request('HEAD', url).ok

    def request(self, method, url, **kwargs):
        # Disable proxies
        kwargs['proxies'] = False
        try:
            response = proxy_requests.request(method, url, **kwargs)
        except proxy_requests.RequestException as err:
            raise ElasticSearchControllerRequestError(err)
        else:
            return response

    def _get_properties(self, model_search):
        opts = model_search.model._meta
        boost = model_search.boost or {}

        properties = {}
        for field in opts.fields:
            field_properties = {
                'store': 'no',
            }

            # Почему не boost.get(): нам не нужно значение, если его вообще нет.
            if field.name in boost:
                field_properties['boost'] = boost[field.name]

            mapping = FIELD_MAPPINGS.get(type(field))
            if mapping is None:
                continue
            field_properties.update(mapping)
            properties[field.name] = field_properties

        return properties
