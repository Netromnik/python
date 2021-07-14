# -*- coding: utf-8 -*-

__all__ = ('login_required',)

from django.contrib.auth.decorators import login_required as base_login_required
from django.core.urlresolvers import reverse_lazy

LOGIN_URL = reverse_lazy('authentication:login')


def login_required(function):
    """Перегруженный декоратор `django.contrib.auth.decorators.login_required',
    чтобы каждый раз не писать имя поля для редиректа"""
    # TODO: перенести в `auth.decorators`

    return base_login_required(function, redirect_field_name='redir', login_url=LOGIN_URL)
