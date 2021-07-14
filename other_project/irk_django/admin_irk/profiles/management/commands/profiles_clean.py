# -*- coding: utf-8 -*-

"""Очистка базы пользователей

Из базы удаляются все пользователи, которые не подтвердили регистрацию
в течение периода подтверждения `django.conf.settings.CONFIRM_PERIOD`

В силу исторических причин есть модели, у которых существуют FK на пользователей с флагом is_active=False.
Таких пользователей не трогаем."""

# TODO: использовать logging вместо print

import datetime

from django.apps import apps
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from irk.authentication import settings as auth_settings
from irk.blogs.models import Author
from irk.profiles.models import Profile, ProfileBannedUser


class Command(BaseCommand):
    attrs = ('user', 'author', 'respondent', 'moderator')
    excludes = (Profile, ProfileBannedUser, Author)

    def handle(self, *args, **options):
        models = []
        for model in apps.get_models():
            if 'django' in model.__module__ or model in self.excludes or User in model._meta.get_parent_list():
                continue

            for attr in self.attrs:
                if hasattr(model, attr):
                    models.append(model)

        dt = datetime.datetime.now() - datetime.timedelta(days=auth_settings.CONFIRM_PERIOD)
        banned_users = list(Profile.objects.filter(user__is_active=False, hash_stamp__lte=dt).values_list('user_id',
                                                                                                          flat=True))
        posted_users = []

        for model in models:
            for attr in self.attrs:
                if hasattr(model, attr):
                    posted_users += model.objects.filter(**{'%s__in' % attr: banned_users}).values_list('%s_id' % attr,
                                                                                                        flat=True)
                    break

        posted_users = list(set(posted_users))

        # Пользователи, которых можно удалять
        loosers = list(set(banned_users) - set(posted_users))

        print '%s users will be deleted, %s users will be saved' % (len(loosers), len(banned_users) - len(loosers))

        Profile.objects.filter(user__in=loosers).delete()
        User.objects.filter(pk__in=loosers).delete()
