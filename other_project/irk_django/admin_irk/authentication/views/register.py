# -*- coding: utf-8 -*-

import datetime
import logging

from django.contrib.auth import login
from django.contrib.auth import login as auth_login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from social_django.utils import load_strategy
from sorl.thumbnail.main import DjangoThumbnail

from irk.authentication import settings as auth_settings
from irk.authentication.forms import SocialAuthenticationForm
from irk.authentication.forms.profile import AvatarUpdateForm
from irk.authentication.forms.register import RegisterForm, SocialRegisterForm
from irk.authentication.tasks import load_user_avatar
from irk.profiles.models import Profile
from irk.utils.http import JsonResponse, get_redirect_url
from irk.utils.notifications import tpl_notify

logger = logging.getLogger(__name__)


def index(request):
    """Главная страница регистрации"""

    next_ = request.GET.get('next')

    if request.user.is_authenticated:
        return HttpResponseRedirect(request.user.profile.get_absolute_url())

    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            profile = Profile(user=user, full_name=form.cleaned_data['name'], comments_notify=True, subscribe=False,
                              is_verified=True)
            profile.create_hash()
            profile.save()

            emails = [form.cleaned_data['email'], ]

            tpl_notify(u'Подтверждение регистрации', 'auth/notif/email_confirm.html', {'profile': profile},
                       emails=emails)

            return HttpResponseRedirect(reverse('authentication:register:confirm_email'))
    else:
        next_ = get_redirect_url(request, request.META.get('HTTP_REFERER', '/'))

        form = RegisterForm()

    context = {
        'next': next_,
        'form': form,
    }

    return render(request, 'auth/register/index.html', context)


def confirm_email(request):
    """Подтверждение email"""
    hash_ = request.GET.get('hash')

    if hash_:
        end_stamp = datetime.datetime.now() - datetime.timedelta(auth_settings.CONFIRM_PERIOD)
        user = get_object_or_404(Profile, hash=hash_, hash_stamp__gte=end_stamp).user
        user.is_active = True
        user.save()
        user.backend = 'authentication.backends.PasswordBackend'
        auth_login(request, user)
        return HttpResponseRedirect(reverse('authentication:register:success'))

    return render(request, 'auth/register/confirm_email.html', {})


def details(request):
    """Ввод дополнительных данных о пользователе

    На этот view пользователь попадает в двух случаях:
        - при первой авторизации через социальную сеть;
        - после ввода номера телефона.
    """

    auth_type = request.session.get(auth_settings.CONFIRM_SESSION_KEY)

    if auth_type not in ('phone', 'social'):
        # TODO: warning, possible hack attempt
        return HttpResponseRedirect(reverse('authentication:register:index'))

    request.session['_auth_new_user'] = True

    return _details_social(request)


def _details_social(request):
    info = request.session[auth_settings.SOCIAL_SESSION_KEY]

    strategy = load_strategy()
    partial_token = request.GET.get('partial_token')
    partial = strategy.partial_load(partial_token)

    if not partial:
        # Есть кейс, когда пользователь после страницы `auth.register.success` нажимает кнопку «Назад» в браузере
        # и попадает обратно на эту страницу. В этот момент в сессии уже нет данных по авторизации
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home_index'))
        return HttpResponseRedirect(reverse('authentication:register:index'))

    backend_name = partial.backend

    backend_complete_url = reverse('social:complete', args=(backend_name,))
    action = None

    if request.user.is_authenticated:
        return HttpResponseRedirect(backend_complete_url)
    if request.POST:
        request.session.set_test_cookie()
        action = request.POST.get('action')
        form = SocialRegisterForm(request.POST, initial=info)
        auth_form = SocialAuthenticationForm(request=request, data=request.POST, backend_name=backend_name)
        if action == 'register' and form.is_valid():
            user = form.save(commit=False)
            request.session['auth_username'] = user.username
            request.session['auth_email'] = user.email
            request.session['auth_name'] = info['name']
            request.session.modified = True

            return HttpResponseRedirect(backend_complete_url)

        elif action == 'auth' and auth_form.is_valid():
            login(request, auth_form.get_user())
            return HttpResponseRedirect(backend_complete_url)

    else:
        form = SocialRegisterForm(initial=info)
        auth_form = SocialAuthenticationForm()

    context = {
        'form': form,
        'auth_form': auth_form,
        'type': 'social',
        'action': action,
        'username': info['name'],
    }

    return render(request, 'auth/register/details.html', context)


def success(request):
    """Сообщение об успешой регистрации"""

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')

    redirect_url = request.POST.get('next')

    if redirect_url:
        return HttpResponseRedirect(redirect_url)

    check_avatar = auth_settings.AVATAR_LOADING_TASK_SESSION_KEY in request.session

    context = {
        'form': AvatarUpdateForm(instance=request.user.profile),
        'check_avatar': check_avatar,
        # Перед редиректом на эту вьюху social_auth очищает содержимое сессии и переносит его в _session_cache
        'next': request.session._session_cache.get('redir') or request.session._session_cache.get('next') or ''
    }

    return render(request, 'auth/register/success.html', context)


def check_avatar_load(request):
    task_id = request.session.get(auth_settings.AVATAR_LOADING_TASK_SESSION_KEY)
    if not task_id:
        return HttpResponseNotFound()

    task = load_user_avatar.AsyncResult(task_id)

    if task.ready():
        request.session.pop(auth_settings.AVATAR_LOADING_TASK_SESSION_KEY)
        thumb = DjangoThumbnail(request.user.profile.image, (50, 50))

        return JsonResponse({
            'status': 200,
            'url': thumb.absolute_url,
        })

    return JsonResponse({
        'status': 404,
    })
