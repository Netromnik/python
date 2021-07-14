# -*- coding: utf-8 -*-

import base64
import datetime
import hashlib
import json
import time
from functools import wraps

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.db.models import Model
from django.db.models.query import QuerySet
from django.http import HttpResponseForbidden as HTTPFB, HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils.http import formatdate
from django.utils.http import is_safe_url

# from .db.kv import get_redis
from .helpers import get_client_ip


class HttpResponseForbidden(HTTPFB):
    def __init__(self, message=''):
        html = render_to_string("404/gagarin.html")
        super(HttpResponseForbidden, self).__init__(html)


class JsonResponse(HttpResponse):
    def __init__(self, object, content_type='application/json', *args, **kwargs):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        elif isinstance(object, Model):
            content = serialize('json', [object])
        else:
            content = json.dumps(object, cls=DjangoJSONEncoder, ensure_ascii=False)

        super(JsonResponse, self).__init__(content, content_type=content_type, *args, **kwargs)


def json_response(func):
    """
    Декоратор для представлений возвращающих JSON.
    После применения декоратора, представление может возвращать списки, словари, объект модели или QuerySet,
    которые будут преобразованы в json.
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)

        return JsonResponse(response)

    return wrapper


def ajax_request(func):
    """
    Декоратор для представлений обрабатывающих AJAX-запросы.
    Входящие данные помещаются в переменную request.json
    Ответ также возвращается в виде json.
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):

        if request.is_ajax():
            try:
                request.json = json.loads(request.body, encoding='utf-8')
            except (ValueError, UnicodeDecodeError):
                request.json = {}
        else:
            return HttpResponseBadRequest()

        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse) and response.status_code != 200:
            return response

        return JsonResponse(response)

    return wrapper


def require_ajax(view):
    """
    Декоратор разрешает только AJAX запросы
    """

    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        if request.is_ajax():
            return view(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest()

    return _wrapped_view


def request_basic_auth(auth_data):
    """ Basic аутентификация для вьюх 
        используется для голосований с everyday.ru
    """

    def wrapper(view_fnc):
        def fnc(request, *args, **kwargs):
            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2:
                    if auth[0].lower() == "basic":
                        name, passwd = base64.b64decode(auth[1]).split(':')
                        if auth_data == (name, passwd):
                            return view_fnc(request, *args, **kwargs)
            return HttpResponseForbidden()

        return fnc

    return wrapper


def set_cache_headers(request, response):
    timestamp = time.mktime((datetime.datetime.now() - datetime.timedelta(hours=1)).timetuple())
    http_date = '%s GMT' % (formatdate(timestamp)[:25])
    path = request.get_full_path()

    if not response.has_header('Cache-Control') or (path.startswith("/adm"), path.startswith("/auth")):
        response['Cache-Control'] = 'no-cache,no-store,max-age=0,must-revalidate'

    if not response.has_header('Expires') or (path.startswith("/adm"), path.startswith("/auth")):
        response['Expires'] = http_date

    if not response.has_header('Last-Modified') or (path.startswith("/adm"), path.startswith("/auth")):
        response['Last-Modified'] = http_date

    return response


def get_redirect_url(request, default=None):
    """Получаем ссылку для редиректа

    Если полученная ссылка не относится к нашему домену (например, попытка перенаправить пользователя на другой сайт),
    возвращается `default`

    В django используется параметр с именем `next`, у нас иногда встречается `redir`. Поддерживаем оба значения.
    """

    params = request.POST if request.POST else request.GET

    url = params.get('next', params.get('redir', '')).strip()
    if is_safe_url(url):
        return url

    if default is not None:
        return default

    return reverse('home_index')


def varnish_cache(ttl):
    def inner_decorator(fn):
        def wrapped(request, *args, **kwargs):
            response = fn(request, *args, **kwargs)
            response['X-Varnish-Age'] = '{0}s'.format(ttl)
            return response

        return wraps(fn)(wrapped)

    return inner_decorator


# def throttling(rpm):
#     """Декоратор для ограничения количества вызовов обернутого view.
#     Позволяет делать `rpm` запросов в минуту
#
#     Параметры::
#         rpm : количество запросов в минуту
#     """
#
#     def inner_decorator(fn):
#         def wrapped(request, *args, **kwargs):
#             cache_key = 'throttle.{0}.{1}'.format(get_client_ip(request),
#                                                   hashlib.sha1(request.get_full_path()).hexdigest())
#             redis = get_redis()
#             requests = int(redis.get(cache_key) or 0)
#             if requests >= rpm:
#                 return HttpResponse(status=429)
#
#             redis.setex(cache_key, 60, requests + 1)
#
#             return fn(request, *args, **kwargs)
#
#         return wraps(fn)(wrapped)
#
#     return inner_decorator
