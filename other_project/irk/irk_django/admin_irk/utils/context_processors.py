# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.messages.api import get_messages


def settings_context(request):
    """Настройки проекта"""

    return {'settings': settings}


def messages_context(request):
    """Пользовательские сообщения"""

    return {'user_messages': get_messages(request)}
