# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime

from django.shortcuts import render
from django.http import Http404
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import SetPasswordForm

from irk.profiles.models import Profile
from irk.utils.notifications import tpl_notify
from irk.authentication import settings as auth_settings


def change(request):
    """Изменение пароля"""

    hash_ = request.GET.get('hash')
    if not hash_:
        raise Http404()

    try:
        user = Profile.objects.get(
            hash=hash_, hash_stamp__gte=datetime.datetime.now() - datetime.timedelta(auth_settings.CONFIRM_PERIOD)
        ).user
    except Profile.DoesNotExist:
        raise Http404()

    if request.POST:
        password_form = SetPasswordForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            user.backend = 'authentication.backends.PasswordBackend'
            auth_login(request, user)
            password = password_form.cleaned_data['new_password1']
            tpl_notify(u'Смена пароля на IRK.ru', 'auth/notif/password_changed.html',
                       {'profile': user.profile, 'password': password}, request, [user.email, ])
            return render(request, 'auth/password_changed.html', {})

    else:
        password_form = SetPasswordForm(user)

    return render(request, 'auth/change_password.html', {'password_form': password_form})


def unsubscribe(request):
    """ Отписка от рассылки новостей """

    hash = request.GET.get('hash') or request.POST.get('hash')
    email = request.GET.get('mail') or request.POST.get('mail')
    try:
        profile = Profile.objects.get(user__email=email, hash=hash,
                                                      hash_stamp__gte=datetime.datetime.now() - datetime.timedelta(
                                                          auth_settings.CONFIRM_PERIOD))
    except Profile.DoesNotExist:
        raise Http404()

    if request.POST and request.POST.get('remove'):
        profile.subscribe = False
        profile.save()
        return render(request, 'auth/unsubscribe_ok.html', {'email': email})
    return render(request, 'auth/unsubscribe.html', {'hash': hash, 'email': email})
