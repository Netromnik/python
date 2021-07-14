# -*- coding: utf-8 -*-

import datetime
import logging

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from irk.ratings import settings as app_settings
from irk.ratings.helpers import is_rateable, is_rated
from irk.ratings.models import RatingObject, Rate, RateableModel
from irk.ratings.tasks import bayes_rating_count
from irk.utils.helpers import iptoint
from irk.utils.http import JsonResponse

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def rate(request):
    """Голосование за объект"""

    data = request.POST
    try:
        content_type = ContentType.objects.get(pk=int(data.get('ct')))
    except (TypeError, ValueError, ContentType.DoesNotExist):
        logger.exception('Invalid content type id: %r' % data.get('ct'), extra={'request': request})
        return HttpResponseForbidden()

    obj_settings = is_rateable('%s.%s' % (content_type.app_label, content_type.model))

    if not obj_settings:
        # За этот объект нельзя голосовать
        logger.error('Unrateable content type %d' % content_type.id, extra={'request': request})
        return HttpResponseForbidden(u'За объект этого типа нельзя голосовать')

    if request.user.is_anonymous and not obj_settings.get('anonymous', False):
        logger.debug('Unallowed anonymous requests. Redirecting to login page now')
        return redirect_to_login(request.get_full_path(), settings.LOGIN_URL, 'next')

    if not obj_settings['type'] in app_settings.RATING_TYPES.keys():
        raise ImproperlyConfigured(u'Нет описания типа голосования')
    rate_range = app_settings.RATING_TYPES[obj_settings['type']]  # Диапазон значений для голосования

    try:
        value = int(data.get('value'))
    except (TypeError, ValueError):
        value = None

    try:
        obed = int(data.get('obed'))
        if obed == 1:
            obed = True
    except (TypeError, ValueError):
        obed = False

    if not value in rate_range:
        logger.error('Invalid rate value %r for content type %d' % (value, content_type.id),
                     extra={'request': request})
        return HttpResponseForbidden(u'Указанное значение недопустимо для данного объекта')

    try:
        obj = content_type.get_object_for_this_type(pk=int(data.get('obj')))
    except (TypeError, ValueError, ObjectDoesNotExist):
        logger.exception('Invalid object id %r for content type %d' % (data.get('obj'), content_type.id),
                         extra={'request': request})
        return HttpResponseForbidden()

    try:
        rate_obj = RatingObject.objects.get(content_type=content_type, object_pk=obj.pk)
    except RatingObject.DoesNotExist:
        logger.debug('Rating object for content type %d and object %r does not exists. Creating now' %
                     (content_type.id, obj.pk))
        rate_obj = RatingObject(content_type=content_type, object_pk=obj.pk)
        rate_obj.save()

    has_rated = is_rated(obj, request)

    if hasattr(obj, 'can_rate') and callable(obj.can_rate) and not obj.can_rate():
        logger.error('Rating for content type %d and object %r is closed' %
                     (content_type.id, obj.pk), extra={'request': request})
        return HttpResponseForbidden(u'Голосование закрыто')

    if not has_rated:
        kwargs = {
            'obj': rate_obj,
            'ip': iptoint(request.META.get('REMOTE_ADDR', 0)),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        if request.user.is_anonymous:
            # Хак для проверки наличия записи, чтобы не вызывать `Duplicate entry` в базе
            if not Rate.objects.filter(**kwargs).exists():
                rate_vote = Rate(value=value, **kwargs)
                rate_vote.save()
                logger.debug('Rate for content type %d, object %r from user %s with value %d' %
                             (content_type.id, obj.pk, request.META.get('REMOTE_ADDR', 0), value))
        else:
            kwargs['user'] = request.user
            if not Rate.objects.filter(**kwargs).exists():
                rate_vote = Rate(value=value, **kwargs)
                logger.debug('Rate for content type %d, object %r from user %d with value %d' %
                             (content_type.id, obj.pk, request.user.id, value))
                rate_vote.save()

        if isinstance(obj, RateableModel):
            bayes_rating_count.delay(obj, rate_obj)

        # Пользователь проголосовал, перечитываем данные о рейтинге
        has_rated = True
        rate_obj = RatingObject.objects.get(pk=rate_obj.pk)

    if request.is_ajax():
        values_range = app_settings.RATING_TYPES[obj_settings['type']]

        if rate_obj and isinstance(obj, RateableModel):
            rate_obj.external = obj.rating
            if rate_obj.total_cnt < app_settings.BAYES_MINIMUM_VOTES:
                rate_obj.external = 0

        if isinstance(obj, RateableModel):
            template_name = obj_settings.get('template', 'ratings/widgets/%s_ext.html' % obj_settings['type'])
        else:
            template_name = obj_settings.get('template', 'ratings/widgets/%s.html' % obj_settings['type'])

        response = JsonResponse({
            'status': 200,
            'content': render_to_string(template_name, {
                'obj': obj,
                'values': values_range,
                'content_type': content_type,
                'is_rated': has_rated,
                'rating': rate_obj,
                'new_makeup2': obed,
                'new_line': obed,
                'min_bayes_votes': app_settings.BAYES_MINIMUM_VOTES,
            }, request=request)
        })

    else:
        response = HttpResponseRedirect(data.get('next', request.META.get('HTTP_REFERER', obj.get_absolute_url())))

    if request.user.is_anonymous:
        cookie_values = []
        for value in request.COOKIES.get(app_settings.COOKIE_NAME, '').split(':'):
            try:
                cookie_values.append(int(value))
            except (TypeError, ValueError):
                continue

        cookie_values.append(rate_obj.pk)
        cookie_values = list(set(cookie_values))

        response.set_cookie(app_settings.COOKIE_NAME, ':'.join([str(x) for x in cookie_values]),
                            expires=datetime.datetime.now() + datetime.timedelta(days=365))

    return response
