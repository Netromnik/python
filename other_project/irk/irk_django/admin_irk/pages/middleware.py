# -*- coding: utf-8 -*-

from django.http import Http404
from django.conf import settings

from irk.pages.views import flatpage
from irk.pages.settings import FLATPAGE_FALLBACK_EXCLUDED_URL
from irk.utils.middleware.http import set_cache_headers


class FlatpageFallbackMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code != 404:
            return response  # No need to check for a flatpage for non-404 responses.

        try:
            # Не проверять flatpage по выбранным url
            for excluded_url in FLATPAGE_FALLBACK_EXCLUDED_URL:
                if request.path_info.startswith(excluded_url):
                    return response

            return set_cache_headers(request, flatpage(request, request.path_info))
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise

            try:
                from utils.exceptions import raven_capture
                raven_capture()
            except ImportError:
                pass

            return response

        # на всякий случай
        return response
