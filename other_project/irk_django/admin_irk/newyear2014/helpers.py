# -*- coding: utf-8 -*-

import datetime
import hashlib


def generate_rotation_key(request):
    """
    Генерация ключа ротации объектов для пользователя.

    Ротация сохраняется для сессии пользователя на 1 день.
    """

    impurity = datetime.date.today().toordinal()
    base_key = request.session.session_key
    # Случается что у анонимов нет ключа сессии
    if not base_key:
        s = u'{}_{}'.format(request.META.get('HTTP_USER_AGENT'), request.META.get('REMOTE_ADDR'))
        base_key = hashlib.md5(s).hexdigest()

    key = u'{}_{}'.format(base_key, impurity)

    return key
