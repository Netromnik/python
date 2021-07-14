# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.contrib.auth.models import Permission, User, Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from irk.comments.models import Comment


def get_moderators():
    """Список модераторов которым разрешено редактировать комментарии"""

    ct = ContentType.objects.get_for_model(Comment)
    perm = Permission.objects.filter(codename='change_comment', content_type=ct).first()
    if not perm:
        return User.objects.none()

    return User.objects.filter(
        Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)
    ).distinct()


def get_email_moderators():
    """Список модераторов которым уходят уведомления"""

    group = Group.objects.filter(name=u'Модераторы комментариев с уведомлениями').first()

    if not group:
        return User.objects.none()

    return group.user_set.filter(is_staff=True)


def get_afisha_email_moderators():
    """Список модераторов которым уходят уведомления из раздела афишы"""

    group = Group.objects.filter(name=u'Модераторы комментариев с уведомлениями от афиши').first()

    if not group:
        return User.objects.none()

    return group.user_set.filter(is_staff=True)


def is_moderator(user):
    """
    Проверка, является ли пользователь модератором.

    :param User user: пользователь
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not user.is_staff:
        return False

    return user.pk in get_moderators().values_list('pk', flat=True)
