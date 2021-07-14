# -*- coding: utf-8 -*-

import hashlib

from django.db import models

try:
    from django.contrib.auth.models import get_hexdigest
except ImportError:
    from irk.authentication.helpers import get_hexdigest


def check_password(user, raw_password):
    """Используется вместо user.check_password(), потому что мы не можем сделать хэшер паролей для sha1-сохраненных
       паролей, сформированных не по схеме sha1$iterations$hash
    """
    try:
        if user.check_password(raw_password):
            return True
    except ValueError:
        pass

    return user.password == hashlib.sha1(raw_password.encode('utf-8')).hexdigest()


def import_cookie(response, source, name='p'):
    if name in source.cookies:
        response.set_cookie(name, source.cookies[name].value, expires=source.cookies[name]['expires'])

    return response


def value_to_form_value(value):
    """ Возвращает значение для формы """
    if isinstance(value, models.Model):  # Т.к. значение передается в форму, то соответственно это должно быть int
        return value.pk
    return value