# -*- coding: utf-8 -*-

from django.contrib.auth import BACKEND_SESSION_KEY


class TemporaryAuthBackendSwitchMiddleware(object):
    """Заменяем старое название бэкенда авторизации на новое

    Эта middleware должна срабатывать раньше 'django.contrib.auth.middleware.AuthenticationMiddleware'
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_backend = request.session.get(BACKEND_SESSION_KEY)
        if auth_backend:
            if auth_backend in ['utils.auth.Backend', 'auth.backends.PasswordBackend']:
                request.session[BACKEND_SESSION_KEY] = 'authentication.backends.PasswordBackend'

            elif 'social_auth.backends' in auth_backend:
                request.session[BACKEND_SESSION_KEY] = auth_backend.replace('social_auth', 'social')

        response = self.get_response(request)

        return response
