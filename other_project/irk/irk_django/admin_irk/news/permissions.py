# -*- coding: utf-8 -*-

from django.db.models import Q
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

from irk.news.models import News, Flash

# Здесь кэшируются функции, определяющие, является ли пользователь модератором новостей раздела
SITE_NEWS_MODERATORS = {}


def get_moderators():
    ct = ContentType.objects.get_for_model(News)
    perm = Permission.objects.filter(codename='change_news', content_type=ct).first()

    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def is_moderator(user):

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_staff and user.has_perm('news.change_news'):
        return True

    return user in get_moderators()


def is_site_news_moderator(request, user=None):
    """Является ли пользователь модератором новостей этого раздела

    Так как у каждого раздела модераторы свои, приходится динамически импортировать функцию
    permissions.is_moderator из каждого раздела, и делать проверку. Все импорты кэшируются"""

    user = user or request.user

    if user.is_anonymous:
        return False

    site_slug = request.csite.slugs
    if not site_slug:
        return False

    if site_slug not in SITE_NEWS_MODERATORS:
        try:
            app_module = __import__('irk.{}.permissions'.format(site_slug), fromlist=['is_moderator'])
        except ImportError:
            SITE_NEWS_MODERATORS[site_slug] = None
        else:
            if hasattr(app_module, 'is_moderator') and callable(app_module.is_moderator):
                SITE_NEWS_MODERATORS[site_slug] = app_module.is_moderator
            else:
                SITE_NEWS_MODERATORS[site_slug] = None

    if SITE_NEWS_MODERATORS[site_slug]:
        return SITE_NEWS_MODERATORS[site_slug](user)

    # Редакторы новстей должны иметь доступ к новостям привязанных к разделам не имеющих собственного permissions
    # например спецпроект 9may
    if is_moderator(user):
        return True

    return False


def get_flash_moderators():
    ct = ContentType.objects.get_for_model(Flash)
    perm = Permission.objects.get(codename='change_flash', content_type=ct)

    return User.objects.filter(Q(is_staff=True), Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


def is_flash_moderator(user):

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_staff and user.has_perm('flash.change_flash'):
        return True

    return user in get_flash_moderators()


def can_see_hidden(user):
    """Может ли пользователь видеть скрытые материалы"""

    return is_moderator(user) or user.has_perm('news.can_see_hidden')
