# -*- coding: utf-8 -*-

import datetime

from irk.utils.http import HttpResponseForbidden
from irk.profiles.models import Profile


def moderator_decorator(func):
    """Декоратор, проверяющий, является ли пользователь модератором раздела или суперпользователем"""

    def decor(request, *args, **kwargs):
        if 'app' in kwargs:
            try:
                app = __import__(kwargs['app'], fromlist=['permissions'])
                if hasattr(app.permissions, 'is_moderator') and app.permissions.is_moderator(request.user):
                    return func(request, *args, **kwargs)
            except ImportError:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()

    return decor


# TODO: docstring класса
# TODO: неправильные отступы и стиль именования класса
class ban_protected(object):
    def check_baned(self, user):
        if not user.is_authenticated:
            return True

        try:
            if user.profile.is_banned:
                now = datetime.datetime.now()
                if not user.profile.bann_end or user.profile.bann_end > now:
                    self.errors['banned'] = u'Ваш аккаунт заблокирован'
                    return False
        except Profile.DoesNotExist:
            pass
        return True


def get_app_moderators(app_label):
    # TODO: docstring
    # TODO: кэшировать результаты импорта
    try:
        app = __import__(app_label, fromlist=['permissions'])
        if hasattr(app, 'permissions') and hasattr(app.permissions, 'get_moderators'):
            return app.permissions.get_moderators()
        return ()
    except ImportError:
        return ()


def is_app_moderator(app_label, user):
    # TODO: docstring
    # TODO: кэшировать результаты импорта
    try:
        app = __import__(app_label, fromlist=['permissions'])
        if hasattr(app, 'permissions') and hasattr(app.permissions, 'is_moderator'):
            return app.permissions.is_moderator(user)
        return False
    except ImportError:
        return False
