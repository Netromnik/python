# -*- coding: utf-8 -*-

import datetime

from django.core.cache import caches
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware as BaseSessionMiddleware
from django.contrib.sessions.backends.base import SessionBase
from django.contrib.sessions.backends.cache import SessionStore as BaseSessionStore
from django.contrib.auth import BACKEND_SESSION_KEY

from irk.utils import settings as local_settings

SESSION_CACHE = caches[settings.SESSION_CACHE_BACKEND]


class DummySessionStore(SessionBase):
    """«Пустой» объект для фиктивного хранения сессий"""

    def __init__(self, *args, **kwargs):
        self._data = {}

    def __contains__(self, *args, **kwargs):
        return False

    def __getitem__(self, key, default=None):
        if key == BACKEND_SESSION_KEY:
            return 'authentication.backends.AnonymousAuthBackend'
        return self._data.get(key, default)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def keys(self):
        return ()

    def items(self):
        return ()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def pop(self, *args, **kwargs):
        return None

    def setdefault(self, *args, **kwargs):
        return None

    def set_test_cookie(self):
        pass

    def test_cookie_worked(self):
        return True

    def _hash(self, *args, **kwargs):
        return None

    def encode(self, *args, **kwargs):
        return ''

    def decode(self, *args, **kwargs):
        return {}

    def _decode_old(self, *args, **kwargs):
        return {}

    def update(self, *args, **kwargs):
        return None

    def has_key(self, *args, **kwargs):
        return False

    def values(self):
        return ()

    def iterkeys(self):
        return ()

    def itervalues(self):
        return ()

    def itemitems(self):
        return ()

    def clear(self):
        pass

    def _get_new_session_key(self):
        return ''

    def _get_session_key(self):
        return ''

    def _set_session_key(self, *args, **kwargs):
        pass

    session_key = property(_get_session_key, _set_session_key)

    def _get_session(self, *args, **kwargs):
        return {}

    _session = property(_get_session)

    def get_expiry_date(self):
        return datetime.datetime.now()

    def set_expiry(self, *args, **kwargs):
        pass

    def get_expire_at_browser_close(self):
        return True

    def flush(self):
        pass

    def cycle_key(self):
        pass

    def exists(self, *args, **kwargs):
        return False

    def create(self):
        pass

    def save(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def load(self):
        pass


class SessionStore(BaseSessionStore):
    """Хранилище сессий в отдельном cache бэкенде"""

    def __init__(self, session_key=None):
        self._cache = SESSION_CACHE
        super(BaseSessionStore, self).__init__(session_key)

    def save(self, *args, **kwargs):
        super(SessionStore, self).save(*args, **kwargs)


class SessionMiddleware(BaseSessionMiddleware):

    def process_response(self, request, response):
        if not hasattr(request, 'session'):
            return response

        is_search_bot = False
        for ua in local_settings.SEARCH_ENGINES_USERAGENTS:
            if ua in request.META.get('HTTP_USER_AGENT', ''):
                is_search_bot = True
                break

        if not is_search_bot:
            response = super(SessionMiddleware, self).process_response(request, response)

            p = request.COOKIES.get('p')
            if p:
                # Продлеваем время жизни куки с настройками пользователя
                response.set_cookie('p', p, expires=datetime.datetime.now()+datetime.timedelta(days=14))

            # Код ниже не совсем понятен. Он вызывает перезапись всего массива данных
            # в редис после каждого запроса. Это вызывает беспонечные перезаписи, на мой
            # взгляд лишние. КРоме того, у нас стал подвисать редис - иногда строка ниже
            # выполняется по 8 секунд и тормозит.
            # Для эсперимента я отключаю эти строки. В худшем случае мы просто потеряем сесси
            # юзеров. Посмотрим, что будет
            # if request.session.keys() and not request.session.get_expire_at_browser_close():
            #     request.session.set_expiry(0)  # TODO: Которое из этих значений нужно оставить?
            #     request.session.set_expiry(None)
            #     request.session.save()

        return response
