# -*- coding: utf-8 -*-

import json
import logging

import rubber
from rubber.response import Response
from rubber.resource import Resource
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_delete

from irk.utils.search.query import ElasticSearchQuerySet
from irk.utils.search.tasks import elasticsearch_update
from irk.utils.core.serializers.geoes import ElasticSearchGEOJSONEncoder


logger = logging.getLogger(__name__)


class ElasticSearchManager(object):

    def __init__(self, model_search):
        self.model_search = model_search

    def get_queryset(self):
        return ElasticSearchQuerySet(self.model_search.model)

    def query(self, params):
        return self.get_queryset().query(params)

    def filter(self, **kwargs):
        return self.get_queryset().filter(**kwargs)

    def raw(self, *args, **kwargs):
        return self.get_queryset().raw(*args, **kwargs)


class ModelSearch(rubber.ElasticSearch):
    fields = ()  # Список сохраняемых полей
    boost = None
    abstract = False  # Не вызывается `self.serialize` при вызове команды `elasticsearch_rebuild`

    def __init__(self, *args, **kwargs):
        kwargs['auto_index'] = False  # Отключаем встроенные сигналы сохранения/удаления
        super(ModelSearch, self).__init__(*args, **kwargs)
        self.raise_on_error = True

    def get_queryset(self):
        return self.model._default_manager.all()

    @staticmethod
    def update_search(instance, **kwargs):
        ct = ContentType.objects.get_for_model(instance)
        pk = getattr(instance, 'pk', None)
        logger.debug('Delaying task with search update for content-type {0} and object pk {1}'.format(ct, pk))

        elasticsearch_update.delay(ct.id, pk)

    def contribute_to_class(self, model, name):
        super(ModelSearch, self).contribute_to_class(model, name)

        setattr(model, name, ElasticSearchManager(self))

        if not settings.TESTS_IN_PROGRESS:
            post_save.connect(self.update_search, sender=model)
            pre_delete.connect(self.update_search, sender=model)

    def makepath(self, name):
        if not name:
            return '/search/{0}_{1}'.format(self.index_name, self.type)

        return '/search/{0}_{1}/{2}'.format(self.index_name, self.type, name)

    def put(self, pk, instance):
        data = self.serialize(pk, instance)

        return Resource(self.makepath(pk), wrapper=Response, raise_on_error=self.raise_on_error).put(data=data)

    def serialize(self, pk, instance):
        if self.fields:
            try:
                data = self.model.objects.filter(pk=pk).values(*self.fields)[0]
            except IndexError:
                logger.error('{} with PK `{}` doesn\'t exists in the database'.format(self.model, pk))
                raise self.model.DoesNotExist()

            data = self.post_serialize(instance, data)
            data = json.dumps(data, cls=ElasticSearchGEOJSONEncoder)
        else:
            data = instance

        return data

    def post_serialize(self, instance, data):
        """Хук, вызываемый после сериализации объекта модели в словарь

        Позволяет добавлять свои поля в index elasticsearch"""

        return data
