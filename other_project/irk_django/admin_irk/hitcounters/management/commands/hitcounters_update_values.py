# -*- coding: utf-8 -*-

import logging
import redis

from django.db.models import F
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from irk.hitcounters.settings import COUNTABLE_OBJECTS, REDIS_DB
from irk.utils.exceptions import raven_capture


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        models = {}
        for model_definition in COUNTABLE_OBJECTS.keys():
            app_name, model_name = model_definition.split('.')
            try:
                model_cls = ContentType.objects.get_by_natural_key(app_name, model_name).model_class()
            except ContentType.DoesNotExist:
                raven_capture('Missing content type for {} {}'.format(app_name, model_name))
                continue

            models[model_definition] = model_cls

        connection = redis.StrictRedis(host=REDIS_DB['HOST'], db=REDIS_DB['DB'])

        for key in connection.keys('object_*'):
            _, obj_type, pk = key.split('_')
            value = connection.get(key)
            connection.delete(key)
            if value is None:
                logger.warning('Got an empty value from key %s. Skipping that object now' % key)
                continue

            logger.debug('Got an value %s from key %s. Deleting it now.' % (value, key))

            model_cls = models.get(obj_type)
            db_field = COUNTABLE_OBJECTS.get(obj_type)

            # Делаем запрос вида UPDATE … SET `db_field` = `db_field` + `value` WHERE id = `pk`;
            params = {
                db_field: F(db_field) + value,
            }
            updated_objects_cnt = model_cls.objects.filter(pk=pk).update(**params)
            logger.debug('Updating object %r %r with %s += %s. Updated objects: %d' % (model_cls, pk, db_field, value,
                                                                                       updated_objects_cnt))
