# -*- coding: utf-8 -*-

from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.utils.decorators import available_attrs


def verification_required(function=None):
    """Декоратор, делающий проверку на авторизированность и верифицированность пользователя"""

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.build_absolute_uri(), settings.LOGIN_URL, REDIRECT_FIELD_NAME)

            if not request.user.profile.is_verified:
                return HttpResponseForbidden()

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def staff_only(func):
    """
    Доступ к вьюшке получат только те, у кого есть доступ в админку
    """
    wrapper = user_passes_test(lambda u: u.is_staff)
    return wrapper(func)
