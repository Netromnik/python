# -*- coding: utf-8 -*-

from __future__ import absolute_import

from social_django.models import UserSocialAuth

from irk.tests.unit_base import UnitTestBase
from irk.profiles.models import Profile


class VerificationTestCase(UnitTestBase):
    """Верификация пользователей"""

    def test(self):
        user = self.create_user('user', 'user', is_verified=False)
        qs = Profile.objects.filter(user=user)
        self.assertFalse(qs.get().is_verified)

        # Привязанный телефон верифицирует пользователя
        profile = qs.get()
        profile.phone = 9501111111
        profile.save()
        self.assertTrue(qs.get().is_verified)

        # Нет ни телефона, ни соцсетей
        profile = qs.get()
        profile.phone = ''
        profile.save()
        self.assertFalse(qs.get().is_verified)

        social = UserSocialAuth(user=user, provider='vk-oauth2', uid='310792822')
        social.save()
        self.assertTrue(qs.get().is_verified)

        social.delete()
        self.assertFalse(qs.get().is_verified)
