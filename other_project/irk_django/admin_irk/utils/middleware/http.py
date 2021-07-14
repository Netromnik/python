# -*- coding: utf-8 -*-

from irk.utils.http import set_cache_headers


class AntiCacheMiddleware(object):
    """Middleware, дополняющее response заголовками, не дающими клиентам и прокси-серверам
    кэшировать ответ"""

    def process_response(self, request, response):
        return set_cache_headers(request, response)
