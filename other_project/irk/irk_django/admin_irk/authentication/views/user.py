# -*- coding: utf-8 -*-

import datetime
import logging

from PIL import Image
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.views import login as django_login_view
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from irk.authentication import settings as auth_settings
from irk.authentication.forms import AuthenticationForm
from irk.authentication.forms.profile import ProfileUpdateForm, PasswordUpdateForm
from irk.authentication.helpers import avatar_resize
from irk.profiles.decorators import login_required
from irk.profiles.models import Profile
from irk.utils.http import JsonResponse, set_cache_headers, get_redirect_url

logger = logging.getLogger(__name__)


def login(request):
    """Авторизация пользователя по E-mail,телефону/паролю"""

    if request.user.is_authenticated:
        return HttpResponseRedirect(get_redirect_url(request, reverse('authentication:profile:update')))

    for key in request.POST:
        # Избавляемся от старой схемы авторизации
        if key.startswith('data[User]'):
            logger.error('Deprecated auth scheme `data[User]` is used', extra={'request': request})
            raise SuspiciousOperation('Deprecated auth scheme. Use `username` and `password` params instead.')

    if request.is_ajax():
        request.session.set_test_cookie()
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            # Если не указано "запомнить меня", то ставим, что сессия кончается по закрытию браузера
            if not form.cleaned_data['remember']:
                request.session.set_expiry(0)

            logger.debug('Successful AJAX authentication', extra={
                'request': request,
            })

            result = [1]
        else:
            logger.warning('Failed AJAX authentication', extra={
                'request': request,
            })
            result = [0, u'Неправильный телефон, E-mail или пароль']

        return JsonResponse(result)

    kwargs = {
        'template_name': 'auth/login.html',
        'redirect_field_name': 'next',
        'authentication_form': AuthenticationForm,
        'extra_context': {
            'next': get_redirect_url(request),
        }
    }

    # django.contrib.auth.views.login ставит свои куки кэширования, заменяем на свои
    return set_cache_headers(request, django_login_view(request, **kwargs))


def logout(request):
    """Выход с сайта"""

    if request.user.is_authenticated:
        logger.debug('Logging out user', extra={
            'request': request,
        })
        auth_logout(request)

    # TODO: ответ для ajax запросов
    return HttpResponseRedirect(get_redirect_url(request))


@login_required
def update(request):
    """Страница с формой загрузки файлов"""

    if request.is_ajax() and request.FILES and 'image_0' in request.FILES:
        image = request.FILES['image_0']
        if not image.content_type in ['image/jpeg', 'image/png']:
            return JsonResponse({'error': u'Недопустимый тип изображеня'})
        if image.size > 300 * 1024:
            return JsonResponse({'error': u'Размер файла превышает 300кб'})
        try:
            tempfile = Image.open(image)
            if tempfile.mode != "RGB":
                tempfile = tempfile.convert("RGB")
            width, height = tempfile.size
        except IOError:
            return JsonResponse({'error': u'Недопустимый тип изображеня'})
        if width < 50 or height < 50:
            return JsonResponse({'error': u'Высота или ширина изображеня менее 50px'})

        image_resized = avatar_resize(tempfile)

        profile = request.user.profile
        profile.image.save(image.name, image_resized, save=False)
        profile.save()
        return JsonResponse({'url': profile.image.url})

    if request.POST:
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            next_ = get_redirect_url(request)
            if next_:
                return HttpResponseRedirect(next_)
            else:
                messages.info(request, u'Изменения успешно сохранены')
                return HttpResponseRedirect('.')

    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'form': form,
    }

    return render(request, 'auth/users/update.html', context)


def update_password(request):
    """Изменение пароля"""

    if not request.user.is_authenticated:
        hash_ = request.GET.get('hash')
        try:
            user = Profile.objects.get(hash=hash_, hash_stamp__gte=datetime.datetime.now() - datetime.timedelta(
                auth_settings.CONFIRM_PERIOD)).user
            user.backend = 'authentication.backends.PasswordBackend'
            auth_login(request, user)
        except Profile.DoesNotExist:
            raise Http404()

    if request.POST:
        form = PasswordUpdateForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            request.user.set_password(password)
            request.user.save()

            return HttpResponseRedirect(reverse('authentication:profile:update'))

    else:
        form = PasswordUpdateForm()

    context = {
        'form': form,
    }

    return render(request, 'auth/users/update_password.html', context)
