# -*- coding: utf-8 -*-

import logging
import redis

from django.core.management.base import BaseCommand
from django.db.models import FieldDoesNotExist, F

from irk.news.models import BaseMaterial
from irk.utils.helpers import int_or_none

from irk.hitcounters.models import MaterialScrollStatistic
from irk.hitcounters.settings import REDIS_DB, READ_TIME_INTERVAL

logger = logging.getLogger(__name__)


# TODO: перенести в приложение statistic
class Command(BaseCommand):
    help = u'Обновить счетчики доскрола для материалов'

    def handle(self, **options):
        logger.info('Start update scroll depth counters')

        connection = redis.StrictRedis(host=REDIS_DB['HOST'], db=REDIS_DB['DB'])

        for key in connection.keys('scroll_depth:material:*'):
            value = int_or_none(connection.get(key)) or 0

            try:
                material_id, field_name = key.split(':')[2:]
            except ValueError:
                logger.debug('Ozzy key {}'.format(key))
                connection.delete(key)
                continue

            if not self._material_is_valid(material_id):
                logger.debug('Material with id {} does not exist'.format(material_id))
                connection.delete(key)
                continue

            if not self._field_is_valid(field_name):
                logger.debug('Field "{}" does not exist'.format(field_name))
                connection.delete(key)
                continue

            value = self._correction(field_name, value)

            kwargs = {
                field_name: F(field_name) + value,
            }

            MaterialScrollStatistic.objects.filter(material_id=material_id).update(**kwargs)
            connection.delete(key)
            logger.debug('Field {} for material {} update successfully'.format(field_name, material_id))

        logger.info('Finish update scroll depth counters')

    def _material_is_valid(self, material_id):
        """Проверить, что идентификатор материала валидный, и создать объект статистики, если его нет"""

        try:
            material_id = int(material_id)
        except ValueError:
            return False

        if not BaseMaterial.objects.filter(pk=material_id).exists():
            return False

        if not MaterialScrollStatistic.objects.filter(material_id=material_id).exists():
            MaterialScrollStatistic.objects.create(material_id=material_id)

        return True

    def _field_is_valid(self, field_name):
        """Проверить, что название поля для хранения счетчика валидно"""

        opts = MaterialScrollStatistic._meta
        try:
            opts.get_field(field_name)
            return True
        except FieldDoesNotExist:
            return False

    def _correction(self, field_name, value):
        """
        Корректировака значений.

        Для разных метрик могут быть свои правила учета.
        """

        if field_name == 'read_time':
            return value * READ_TIME_INTERVAL

        return value
