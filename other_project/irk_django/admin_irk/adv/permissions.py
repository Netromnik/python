from django.db.models import Q
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from .models import Log
from about.models import Pricefile


def get_moderators():
    ct = ContentType.objects.get_for_model(Log)
    perm = Permission.objects.get(codename='add_log', content_type=ct)
    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def get_sellers():
    ct = ContentType.objects.get_for_model(Pricefile)
    perm = Permission.objects.get(codename='change_pricefile', content_type=ct)
    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def is_moderator(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_staff:
        return user in get_moderators()

    return False