# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from social_django.models import UserSocialAuth
from social_django.utils import psa

from irk.authentication.helpers import deauth_users
from irk.comments.permissions import is_moderator
from irk.utils.http import JsonResponse

logger = logging.getLogger(__name__)


def error(request):
    """Ошибка в процессе авторизации"""

    storage = get_messages(request)
    list(storage)

    if request.is_ajax():
        return JsonResponse({'code': 403})

    return render(request, 'auth/social/error.html')


def error_inactive(request):
    """
    Показывает ошибку тем юзерам, у которых is_active=False после возвращения
    с авторизации через соцсети

    Показывает ошибку и кнопку Написать в редакцию. При нажатии, пользователь
    попадает на страницу фидбека, где текст в поле Вопрос автоматически вставлен.
    """
    user = request.GET.get('user')
    if user:
        msg = 'Здравствуйте.\n\n' \
              'Я хочу восстановить аккаунт №{}. Сейчас он деактивирован ' \
              'и я не могу войти на сайт.\n\n'.format(user)
    else:
        # сюда не должно доходить выполнение, но всё же
        msg = 'Здравствуйте.\n\n' \
              'Я не могу войти в свой аккаунт из соцсетей.\n\n' \
              '<вставьте ссылку на вашу страницу соцсети, через которую не получается войти>.'

    return render(request, 'auth/social/error_inactive.html', {'msg': msg})


@never_cache
@login_required
@psa()
@require_POST
@csrf_protect
def disconnect(request, backend, user_id, association_id=None):
    """Disconnects given backend from current logged in user."""

    if not is_moderator(request.user):
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=user_id)
    do_revoke = getattr(settings, 'SOCIAL_AUTH_REVOKE_TOKENS_ON_DISCONNECT', None)

    filter_args = {}
    if association_id:
        filter_args['id'] = association_id
    else:
        filter_args['provider'] = backend

    instances = UserSocialAuth.get_social_auth_for_user(user).filter(**filter_args)

    if do_revoke:
        for instance in instances:
            instance.revoke_token(drop_token=False)

    instances.delete()

    deauth_users([user_id])

    url = request.POST.get(REDIRECT_FIELD_NAME, '/')
    return HttpResponseRedirect(url)
