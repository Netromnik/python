# -*- coding: utf-8 -*-

from django.db.models import Q
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from irk.obed.models import Establishment, Article


def get_moderators():
    ct = ContentType.objects.get_for_model(Establishment)
    perm = Permission.objects.get(codename='change_establishment', content_type=ct)
    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def is_moderator(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_staff:
        return user in get_moderators()

    return False


def can_edit_establishment(user, establishment):
    if establishment and establishment.user == user:
        return True

    return establishment.user == user or is_moderator(user)


def can_edit_news(user):
    """Возможность редактирования новостей обеда"""

    if user.is_anonymous:
        return False

    if user.is_superuser:
        return True

    ct = ContentType.objects.get_for_model(Article)
    perm = Permission.objects.get(codename='change_article', content_type=ct)

    return user in User.objects.filter(Q(is_staff=True),
                                       Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()
