# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import logging
import redis

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.models import F

from irk.hitcounters.settings import REDIS_DB
from irk.utils.helpers import int_or_none

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Обновление счетчиков просмотров по дням. \n\n' \
           'Сохранение счетчиков осуществляется функцией hitcounter_by_day. \n' \
           'Для хранения статистики в БД, объект модели должен обладать полем statistic, являющимся RelatedField ' \
           'на модель с полями (date, views).'

    def handle(self, **options):
        logger.debug('Start update hitcounters by day')

        connection = redis.StrictRedis(host=REDIS_DB['HOST'], db=REDIS_DB['DB'])

        for key in connection.keys('hitcounter_by_day*'):
            value = connection.get(key)
            connection.delete(key)
            if value is None:
                logger.warning('Got an empty value from key {}. Skipping that object now'.format(key))
                continue

            self._update_counters(key, value)

        logger.debug('Finish update hitcounters by day')

    def _update_counters(self, key, value):
        """Обновление счетчиков просмотра"""

        date_ordinal, app_label, model_name, pk = self._parse(key)

        if not all([date_ordinal, app_label, model_name, pk]):
            logger.error('Key does not have required parts: {}'.format(key))
            return

        try:
            ct = ContentType.objects.get_by_natural_key(app_label, model_name)
            obj = ct.get_object_for_this_type(pk=pk)
        except ObjectDoesNotExist:
            logger.error('Object {}.{} with id {} does not exist'.format(app_label, model_name, pk))
            return

        if not hasattr(obj, 'statistic'):
            logger.error('Object {} has not field "statistic"')
            return

        dt = datetime.date.fromordinal(date_ordinal)
        if not obj.statistic.filter(date=dt).exists():
            obj.statistic.create(date=dt)

        obj.statistic.filter(date=dt).update(views=F('views') + value)

        logger.debug('Success update statistic for key: {}'.format(key))

    def _parse(self, key):
        """
        Разобрать key.

        Ключ должен быть вида hitcounter_by_day:735856:discounts.offer:59, где
            hitcounter_by_day - название функции
            735856 - порядковый номер даты (вызов метода date.toordinal())
            discounts.offer - полное название модели (app_label.model_name)
            59 - идентификатор объекта

        :rtype: tuple
        :return: (порядковый номер даты, название приложения, название модели, идентификатор)
        """

        try:
            _, date_ordinal, app_model_name, pk = key.split(':')
            app_label, model_name = app_model_name.split('.')
        except ValueError:
            logger.error('Invalid key: {}'.format(key))
            return [None] * 4

        return int_or_none(date_ordinal), app_label, model_name, pk
