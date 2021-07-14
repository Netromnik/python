# -*- coding: utf-8 -*-

import logging
import types
import urllib

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.utils.itercompat import is_iterable

from irk.utils.notifications import tpl_notify
from irk.utils.http import JsonResponse, ajax_request
from irk.utils.helpers import get_object_or_none

from irk.profiles.models import Profile
from irk.profiles.helpers import import_cookie, value_to_form_value
from irk.profiles.options import options_library
from irk.profiles.controllers import BanController


logger = logging.getLogger(__name__)


@user_passes_test(lambda u: u.has_perm('comments.change_comment'))
@require_POST
@ajax_request
def ban(request, user_id):
    """Забанить/разблокировать пользователя

    Ожидаемый формат данных:
    {
        'action': 'ban',  // команда. Поддерживаемые: ban, unban, spam. Required.
        'period': 7,      // количество дней бана
        'reason': '',     // причина бана
        'next': '',       // url для редиректа
        'message_id': null   // id сообщения, которое нужно удалить после бана пльзователя
    }
    Обязательным является только параметр action.
    """

    user = get_object_or_none(User, pk=user_id)
    if not user:
        return {'ok': False, 'msg': u'Нет пользователя с идентификатором {}'.format(user_id)}

    action = request.json.get('action')
    if not action:
        return {'ok': False, 'msg': u'Нет обязательного параметра action'}

    message_id = request.json.get('message_id')
    period = request.json.get('period')
    reason = request.json.get('reason', '')
    next_url = request.json.get('next')

    controller = BanController(moderator=request.user)

    if action == 'ban':
        controller.ban(user, period=period, reason=reason)
        controller.delete_message(message_id)
        result_msg = u'Пользователь забанен'
    elif action == 'spam':
        controller.ban(user, reason=reason)
        controller.delete_all_user_messages(user)
        result_msg = u'Пользователь забанен за спам'
    elif action == 'unban':
        controller.unban(user)
        result_msg = u'Пользователь разблокирован'
    else:
        return {'ok': False, 'msg': u'Неизвестная команда команда {}'.format(action)}

    if action in ['ban', 'spam']:
        tpl_notify(
            u'Ваш аккаунт на Ирк.ру заблокирован', 'notif/ban.html', {'user': user, 'period': period},
            request, [user.email]
        )
    elif action == 'unban':
        tpl_notify(u'Ваш аккаунт на Ирк.ру разблокирован', "notif/unban.html", {'user': user}, request, [user.email])
    else:
        pass

    return {'ok': True, 'msg': result_msg, 'redirect': next_url}


def multiple_options(request):
    """Сохранение нескольких настроек пользователя за раз

    Входящие данные:
        next:
            Адрес для переадресации (не для AJAX запросов)

        with_response:
            Клиент, осуществивший ответ, ожидает, что после сохранения опций сервер отдаст блоки данных
            для каждой опции.
            Возвращается JSON словарь, где ключом является название опции, а значением - результат работы
            метода render() каждой опции

        flat:
            Возвращается отрендеренное значение только одного, последнего user option
            Используется только вместе с параметром with_response

        Все остальные пары ключ=значение считаются данными опций.
        Множественные значения записываются через запятую.

    При успешном сохранении всех настроек возвращается словарь {'success': true}

    При ошибке сохранения возвращается словарь {'success': false, 'errors': []},
        где errors - массив имен настроек, которые не удалось сохранить
    """

    data = (request.POST or request.GET).copy()  # mutable-копия

    if 'next' in data:
        # URL для редиректа
        next_ = urllib.unquote(data['next'])
        data.pop('next')
    else:
        next_ = None

    if 'with_response' in data:
        with_response = True
        data.pop('with_response')
    else:
        with_response = False

    # Рендерится только один, последний user_option
    if 'flat' in data:
        flat_render = True
        data.pop('flat')
    else:
        flat_render = False

    if not data:
        return HttpResponseBadRequest()

    # Список настроек, не прошедших сохранение
    errors = []

    # Объект передается всем настройкам для сохранения cookie в него
    # После сохранения всех настроек, cookie со значениями передается в нормальный response
    fake_response = HttpResponse()

    # Ответ клиенту с отрендеренными данными опций
    response_data = {}
    # Дополнительный контент для рендеринга
    extra = {
        'next': next_ or request.META.get('HTTP_REFERER')
    }

    prepared_options = {}
    for idx, (key, value) in enumerate(data.items()):
        try:
            param = options_library[key](request, response=fake_response)
        except KeyError:
            logger.exception('Option with name `%s` is not avaliable. Ur %s' % (key, request.get_full_path()),
                             extra={'request': request})
            errors.append(key)
            continue

        prepared_options[key] = param

    for idx, (key, value) in enumerate(data.items()):
        if not key in prepared_options:
            continue

        param = prepared_options[key]

        try:
            value = param.load_value_from_input(value)
        except ValueError:
            value = param.default
            if is_iterable(value):
                value = map(value_to_form_value, value)
            else:
                value = value_to_form_value(value)

        form = param.form(data={'param': key, 'value': value, 'next': next_})
        if form.is_valid():
            param.value = form.cleaned_data['value']
            param.save()

            # Обновляем request у всех опций
            for p in prepared_options.values():
                p.request = param.request

            if with_response:
                if not flat_render:
                    try:
                        response_data[key] = param.render(extra)
                    except NotImplementedError:
                        logger.info(u'User option `%s`\'s method `render` is not implemented' % key)
                else:
                    try:
                        response_data = {'success': True, 'html': param.render(extra)}
                    except NotImplementedError:
                        logger.info(u'User option `%s`\'s method `render` is not implemented' % key)
        else:
            logger.info('Form for option `%s` is not valid' % key)
            errors.append(key)
            continue

    if request.is_ajax():
        if with_response:
            response = JsonResponse(response_data)
        else:
            response = JsonResponse({'success': True})
    else:
        response = HttpResponseRedirect(next_ if next_ else request.META.get('HTTP_REFERER', '/'))

    # Подменяем cookie
    response = import_cookie(response, fake_response)

    return response


def set_option(request):
    """Сохранение настроек пользователя"""

    if request.POST:
        # Хак для переадресации на вьюшку, обрабатывающую несколько опций за раз
        if not 'param' in request.POST and not 'value' in request.POST:
            return multiple_options(request)
        param = request.POST.get('param')
        with_response = 'with_response' in request.POST
    else:
        if not 'param' in request.GET and not 'value' in request.GET:
            return multiple_options(request)
        param = request.GET.get('param')
        with_response = 'with_response' in request.GET

    fake_response = HttpResponse()

    if not param:
        return HttpResponseBadRequest(u'Нет параметра param')
    else:
        try:
            param = options_library[param](request, response=fake_response)
        except KeyError:
            raise Http404()

    if request.POST:
        form = param.get_form(data=request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']
            param.value = value
            param.save()

            if request.is_ajax():
                if with_response:
                    try:
                        response = HttpResponse(param.render())
                        response = import_cookie(response, fake_response)

                        return response
                    except NotImplementedError:
                        logger.info(u'User option `%s`\'s method `render` is not implemented' % param.name)
                response = JsonResponse({'success': True})
                response = import_cookie(response, fake_response)
                return response

            response = HttpResponseRedirect(form.cleaned_data.get('next', '/'))
            response = import_cookie(response, fake_response)

            return response

    else:
        next_ = request.GET.get('next', '/')

        try:
            value = urllib.unquote(request.GET.get('value'))
        except (TypeError, ValueError, AttributeError):
            value = None
        if not value:
            param.value = param.default
            param.save()

            if request.is_ajax():
                response = JsonResponse({'success': True})
                response = import_cookie(response, fake_response)

                return response
            response = HttpResponseRedirect(next_)
            response = import_cookie(response, fake_response)

            return response

        if param.multiple:
            try:
                values = map(int, request.GET.getlist('value'))
            except:
                values = []

            if len(values) <= 1:
                try:
                    values = map(int, value.split(','))
                except ValueError:
                    values = []

            if isinstance(param.choices, QuerySet):
                values = param.choices.filter(pk__in=values)
            elif isinstance(param.choices, (types.TupleType, types.ListType)):
                clean_values = []
                choices_values = [x[0] for x in param.choices]
                for value in values:
                    if value in choices_values:
                        clean_values.append(value)
                values = clean_values
            param.value = values
            param.save()

        else:
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = 0
            if isinstance(param.choices, QuerySet):
                try:
                    value = param.choices.get(pk=value)
                except ObjectDoesNotExist:
                    value = param.default
            param.value = value
            param.save()

        if request.is_ajax():
            if with_response:
                try:
                    response = HttpResponse(param.render())
                    response = import_cookie(response, fake_response)

                    return response
                except NotImplementedError:
                    logger.info(u'User option `%s`\'s method `render` is not implemented' % param.name)
            response = JsonResponse({'success': True})
            response = import_cookie(response, fake_response)

            return response
        response = HttpResponseRedirect(next_)
        response = import_cookie(response, fake_response)

        return response

    if request.is_ajax():
        return JsonResponse({'success': False})
    return HttpResponseRedirect(request.GET.get('next', '/'))


@require_POST
@ajax_request
def close(request, profile_id):
    """Закрыть профиль пользователя."""

    profile = get_object_or_none(Profile, id=profile_id)
    if not profile:
        return {'ok': False, 'msg': u'Профиль не найден'}

    if profile.user == request.user:
        profile.is_closed = True
        profile.save()
        profile.user.is_active = False
        profile.user.save()

        auth_logout(request)

        return {'ok': True, 'msg': u'Профиль пользователя закрыт'}

    return {'ok': False, 'msg': u'Нет прав на закрытие профиля'}
