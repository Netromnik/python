# -*- coding: utf-8 -*-

import logging

from django.contrib.auth.models import User
from django.shortcuts import render

from irk.authentication import settings as app_settings
from irk.authentication.forms import RemindForm
from irk.utils.http import JsonResponse
from irk.utils.notifications import tpl_notify

logger = logging.getLogger(__name__)


def index(request):
    """Восстановление пароля"""

    request.session.pop(app_settings.CONFIRM_SESSION_KEY, None)
    request.session.pop(app_settings.PHONE_SESSION_KEY, None)

    message = ''

    if request.POST:
        form = RemindForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if user:
                user.profile.create_hash()
                user.profile.save()
                tpl_notify(u'Восстановление пароля', 'auth/notif/remind.html', {'profile': user.profile}, request,
                           [user.email])
            if request.is_ajax():
                return JsonResponse({'success': True, 'is_phone': False})
            else:
                return render(request, 'auth/remind_ok.html', {})
        else:
            message = form.errors
            if request.is_ajax():
                return JsonResponse({'success': False, 'message': message})
    else:
        form = RemindForm()

    context = {
        'form': form,
        'message': message,
    }

    return render(request, 'auth/remind.html', context)
