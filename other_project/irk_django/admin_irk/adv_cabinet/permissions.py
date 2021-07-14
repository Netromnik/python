# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from functools import wraps

from django.shortcuts import redirect
from rest_framework import permissions


class IsBusinessAccount(permissions.BasePermission):
    """Проверка на наличие бизнес аккаунта для DRF"""

    def has_permission(self, request, view):
        return request.user.profile.is_business_account()


def business_account_required(function):
    """Проверка на наличие бизнес аккаунта для простых view"""

    @wraps(function)
    def wrapper(request, *args, **kw):
        if not request.user.is_authenticated():
            return redirect('home_index')

        if request.user.profile.is_business_account():
            return function(request, *args, **kw)

        return redirect('home_index')

    return wrapper
