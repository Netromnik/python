# -*- coding: utf-8 -*-

from django.db.models import Q
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from irk.tourism.models import TourFirm, Place, News
from irk.phones.permissions import get_moderators as get_phones_moderators


class TourPermException(Exception):
    pass


def get_moderators():
    ct = ContentType.objects.get_for_model(Place)
    perm = Permission.objects.get(codename='change_place', content_type=ct)

    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def get_editorials():
    """Список пользователей, которые могут создавать гостиницы"""

    users_ids = filter(lambda x: x, TourFirm.objects.filter(firm__visible=True).values_list('firm__user', flat=True))
    return User.objects.filter(Q(pk__in=users_ids) | Q(is_superuser=True))


def is_moderator(user,):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_staff:
        return user in get_moderators()

    return False


def can_edit_tours(user, firm):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    try:
        if user == firm.user:
            return True
        else:
            raise TourPermException()
    except:
        return user in get_moderators()


def can_edit_firm(user, firm):
    if user.is_superuser:
        return True

    try:
        if user == firm.user:
            return True
        else:
            raise Exception()
    except:
        return user in get_phones_moderators()


def can_edit_news(user):
    """Возможность редактирования новостей туризма"""

    if user.is_anonymous:
        return False

    if user.is_superuser:
        return True

    ct = ContentType.objects.get_for_model(News)
    perm = Permission.objects.get(codename='change_news', content_type=ct)

    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) |
                                                 Q(groups__permissions=perm), pk=user.pk).count() > 0
