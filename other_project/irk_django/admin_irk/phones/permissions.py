# -*- coding: UTF-8 -*-

from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from django.db.models.query import Q

from irk.phones.models import Firms


def get_moderators():
    ctype = ContentType.objects.get_for_model(Firms)
    perm = Permission.objects.get(codename='change_firms', content_type=ctype)
    return User.objects.filter(
        Q(is_staff=True),
        Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def is_moderator(user,):

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_staff and user.has_perm("phones.change_firms"):
        return True

    perm = Permission.objects.get(
        codename='change_firms',
        content_type=ContentType.objects.get_for_model(Firms))
    return user.is_staff and user.groups.filter(
        permissions=perm).count() > 0


def has_edit_firm_perm(user, firm):
    try:
        return firm.user == user
    except:
        return False


def can_edit_firm(firm, user):
    try:
        if firm.user == user:
            return True
    except User.DoesNotExist:
        pass

    if is_moderator(user):
        return True

    return False


def can_edit_firm_decorator(func):
    """ Декоратор для определеня, имеет ли пользователь
        права на редактирование объявления.
    """

    def decor(request, id):
        firm = Firms.objects.get(pk=int(id))
        if is_moderator(request.user) or has_edit_firm_perm(request.user, firm):
            return func(request, id)
        else:
            return HttpResponseRedirect(firm.get_absolute_url())
    return decor
