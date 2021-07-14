# -*- coding: utf-8 -*-

import hashlib
import logging
import datetime
import redis

from django.conf import settings

from irk.hitcounters.settings import USER_KEY_EXPIRE, REDIS_DB
from irk.hitcounters.helpers import get_hitcounter_info


logger = logging.getLogger(__name__)


def _object_key(obj):
    info = get_hitcounter_info(obj)
    if not info:
        return

    return 'object_%s_%s' % (info['obj_type'], obj.pk)


def _user_key(request, obj_key):
    from irk.utils.helpers import get_client_ip

    ip = get_client_ip(request)
    ua = hashlib.sha1(request.META.get('HTTP_USER_AGENT', '')).hexdigest()

    return '%s_%s_%s' % (ip, ua, obj_key)


def increase_counter(obj_key, user_key):
    """
    Увеличить счетчик просмотров для пользователя.

    :param obj_key: ключ объекта
    :param user_key: ключ пользователя
    """

    connection = redis.StrictRedis(host=REDIS_DB['HOST'], db=REDIS_DB['DB'])

    # Пользователь еще не просматривал данный объект за X время
    if user_key not in connection:
        logger.debug('User with key `%s` not exist, creating it now with value = 1', user_key)
        p = connection.pipeline()
        p.setex(user_key, USER_KEY_EXPIRE, 1)
        p.incr(obj_key)
        p.execute()
    else:
        # Иначе обновляем время жизни ключа пользователя.
        connection.expire(user_key, USER_KEY_EXPIRE)
        logger.debug('Key hit `%s` for user, value will not be updated', user_key)


def hitcounter(request, obj):
    """Засчитать показ объекта

    Параметры::

        :param request: `django.http.HttpRequest'
        :param obj: объект любой модели, перечисленной в `hitcounters.settings.COUNTABLE_OBJECTS.keys()'
    """

    if getattr(settings, 'DISABLE_HITCOUNTERS', False):
        return

    obj_key = _object_key(obj)
    user_key = _user_key(request, obj_key)

    increase_counter(obj_key, user_key)


def hitcounter2(request, obj):
    """
    Вторая версия счетчика просмотров, работающая через ClickHouse
    """
    if getattr(settings, 'DISABLE_HITCOUNTERS', False):
        return

    # Пока заглушено
    # почему-то не хочет импортироваться наверху
    # from irk.hitcounters.clickhouse import save_page_view
    # save_page_view(request, obj)


def hitcounter_by_day(request, obj):
    """Увеличение счетчиков показов по дням"""

    # date_ordinal - порядковый номер дня (результат метода date.toordinal())
    # model_name - полное название модели (app_label.model_name)
    # pk - идентификатор объекта
    key_pattern = u'hitcounter_by_day:{date_ordinal}:{app_model_name}:{pk}'
    date_ordinal = datetime.date.today().toordinal()
    app_model_name = unicode(obj._meta)

    obj_key = key_pattern.format(date_ordinal=date_ordinal, app_model_name=app_model_name, pk=obj.pk)
    user_key = _user_key(request, obj_key)

    increase_counter(obj_key, user_key)
