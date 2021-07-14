# -*- coding: utf-8 -*-

from django.contrib.auth.models import User, Permission
from django.db.models.query import Q
from django.contrib.contenttypes.models import ContentType

from irk.experts.models import Expert


def can_reply(user, expert):
    """Пользователь `user' может отвечать на вопросы к конференции `expert'"""

    if user.is_anonymous:
        return False

    if user.is_superuser or user == expert.user:
        return True

    return user in get_moderators()


def can_delete(user):
    """Пользователь `user' может удалять вопросы в конференции `expert'

    Главное отличие: ведущий конференции не может удалять вопросы
    """

    if user.is_anonymous:
        return False

    if user.is_superuser:
        return True

    return user in get_moderators()


def get_moderators():
    """Модераторы эксперта"""

    ct = ContentType.objects.get_for_model(Expert)
    perm = Permission.objects.get(codename='change_expert', content_type=ct)

    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def is_moderator(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_staff and user.has_perm('experts.change_expert'):
        return True

    return user in get_moderators()
