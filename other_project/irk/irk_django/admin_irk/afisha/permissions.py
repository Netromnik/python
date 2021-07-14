# -*- coding: utf-8 -*-

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import Q

from irk.afisha.models import Event
from irk.news.models import News


def get_moderators():
    perm = Permission.objects.get(codename='change_event', content_type=ContentType.objects.get_for_model(Event))
    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def is_moderator(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user in get_moderators()


def is_news_moderator(user):
    """Модератор новостей афиши"""

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_staff and user.has_perm('afisha.change_news'):
        return True

    perm = Permission.objects.get(codename='change_news', content_type=ContentType.objects.get_for_model(News))

    return user.is_staff and user.groups.filter(permissions=perm).count() > 0
