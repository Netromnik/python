# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from social_django.models import UserSocialAuth

from irk.profiles.models import Profile


class Command(BaseCommand):
    """Проверка верифицированности всех пользователей"""

    def handle(self, *args, **kwargs):
        for profile_id, user_id, phone in Profile.objects.values_list('id', 'user_id', 'phone'):
            is_verified = bool(phone) \
                          or UserSocialAuth.objects.filter(user_id=user_id).exists() \
                          or bool(User.objects.filter(id=user_id).values_list('is_staff', flat=True)[0])

            Profile.objects.filter(id=profile_id).update(is_verified=is_verified)
