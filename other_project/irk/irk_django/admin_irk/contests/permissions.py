# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group, User


def get_moderators():
    """Получить модераторов конкурсов"""

    group = Group.objects.filter(name=u'Модераторы конкурсов').first()
    if not group:
        return User.objects.none()

    return group.user_set.filter(is_staff=True)


def is_moderator(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user in get_moderators()
