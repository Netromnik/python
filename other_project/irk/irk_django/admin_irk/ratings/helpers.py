# -*- coding: utf-8 -*-

import types

from django.db.models import Model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from irk.ratings import settings
from irk.ratings.models import RatingObject, Rate
from irk.utils.helpers import iptoint
from irk.utils.metrics import newrelic_record_timing, NewrelicTimingMetric


@newrelic_record_timing('Custom/Ratings/IsRateable')
def is_rateable(obj, for_anonymous=False):
    """Проверка, можно ли оценивать переданный объект

    Параметры::
        obj - объект для голосования
    """

    if not isinstance(obj, (Model, types.StringType, types.UnicodeType)):
        raise ValueError(u'Невозможно определить, можно ли проголосовать за объект `%s`' % obj)

    if isinstance(obj, Model):
        # Передана модель, нужно искать ContentType
        try:
            content_type = ContentType.objects.get_for_model(obj)
        except ContentType.DoesNotExist:
            return False
        obj = '%s.%s' % (content_type.app_label, content_type.model)

    for key, pattern in settings.RATEABLE_OBJECTS.items():
        if obj.lower() == key.lower():
            return pattern

    return False


@newrelic_record_timing('Custom/Ratings/IsRated')
def is_rated(obj, request, user=None):
    """Пользователь уже голосовал за объект"""

    user = user or request.user

    pattern = is_rateable(obj)

    content_type = ContentType.objects.get_for_model(obj)

    if user.is_anonymous:
        with NewrelicTimingMetric('Custom/Ratings/IsRatedAnonymous'):
            # Анонимные пользователи

            if not pattern.get('anonymous', False):
                # Анонимам голосовать нельзя
                return True

            try:
                rating_object_id = RatingObject.objects.filter(object_pk=obj.pk, content_type=content_type.pk).\
                    values_list('id', flat=True)[0]
            except IndexError:
                return False

            rate_exists = Rate.objects.filter(obj__id=rating_object_id, ip=iptoint(request.META.get('REMOTE_ADDR', 0)),
                                              user_agent=request.META.get('HTTP_USER_AGENT', '')).exists()

            if rate_exists:
                return True

            # Смотрим в cookie, голосовал ли пользователь
            return str(rating_object_id) in request.COOKIES.get(settings.COOKIE_NAME, '').split(':')

    with NewrelicTimingMetric('Custom/Ratings/IsRatedAuthenticated'):
        # Забанен - не голосуешь!
        if user.profile and (user.profile.is_banned or not user.profile.is_verified):
            return True

        # Пользователь не может голосовать за свой объект
        try:
            if 'user_fk' in pattern and getattr(obj, pattern['user_fk']) == user:
                return True
        except User.DoesNotExist:
            return False

        return Rate.objects.filter(user=user, obj__object_pk=obj.pk, obj__content_type=content_type.pk).exists()
