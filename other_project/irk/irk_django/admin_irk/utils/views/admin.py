# -*- coding: utf-8 -*-

import redis

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import linebreaks

from irk.utils.http import JsonResponse
from irk.utils.text.processors.default import processor

BASE_KEY = 'admin:edit-locks:%s'


@user_passes_test(lambda x: x.is_active and x.is_staff)
def edit_notification(request):
    """На страницах админки показываем уведомление, если эту страницу открыл кто-то еще из админов"""

    key = BASE_KEY % request.GET.get('key', '').strip()

    db = settings.REDIS['default']
    client = redis.StrictRedis(host=db['HOST'], db=db['DB'])

    users_locks = client.keys('%s:*' % key)  # Пользователи, просматривающие эту страницу

    # Ставим лок на эту страницу для текущего пользователя
    client.setex('%s:%s' % (key, request.user.id), 30, request.user.get_full_name())
    if not users_locks:
        return JsonResponse([])

    user_ids = [int(x.replace(key, '').lstrip(':')) for x in users_locks]
    usernames = client.mget(users_locks)

    del client  # Закрываем соединение с redis пораньше

    users = dict(zip(user_ids, usernames))
    try:
        del users[request.user.id]
    except KeyError:
        pass

    return JsonResponse(users.values())


@csrf_exempt
def sandbox(request):
    if request.POST:
        content = request.POST.get('content', '')
        errors = []
        for tag_type, tag_name, context in processor.validate(content):
            message = []
            if tag_type == processor.TOKEN_TAG_START:
                message.append(u'Обнаружен лишний открывающий BB код')
            elif tag_type == processor.TOKEN_TAG_END:
                message.append(u'Обнаружен лишний закрывающий BB код')
            message.append(tag_name)
            message.append(context)

            errors.append(message)

        return JsonResponse({
            'content': linebreaks(processor.format(content)),
            'errors': errors,
        })

    return render(request, 'admin/sandbox.html', {
        'title': u'Справка по типографу',
    })
