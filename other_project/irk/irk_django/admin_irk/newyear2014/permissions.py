# -*- coding: utf-8 -*-

from django.db.models import Q
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

from irk.newyear2014.models import Horoscope


def get_moderators():
    ct = ContentType.objects.get_for_model(Horoscope)
    perm = Permission.objects.get(codename='change_horoscope', content_type=ct)
    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def is_moderator(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_staff:
        return user in get_moderators()

    return False
