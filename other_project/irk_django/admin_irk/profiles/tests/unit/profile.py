# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase
from irk.profiles.models import Profile


class CloseProfileTest(UnitTestBase):
    """Тесты закрытия профиля пользователя"""

    csrf_checks = False

    def setUp(self):
        self._owner = self.create_user('owner')
        self._moderator = self.create_user('moderator', is_admin=True)
        self._hacker = self.create_user('hacker')
        self._profile = self._owner.profile
        self._url = reverse('profiles:close', kwargs={'profile_id': self._profile.id})

    def test_for_owner_profile(self):
        """Закрывает владелец профиля"""

        self._check_is_opened()

        response = self.app.post(self._url, user=self._owner, xhr=True)

        self.assertStatusIsOk(response)
        self.assertTrue(response.json['ok'])
        self._check_is_closed()

    def test_for_hacker(self):
        """Пытается закрыть хакер"""

        self._check_is_opened()

        response = self.app.post(self._url, user=self._hacker, xhr=True)

        self.assertStatusIsOk(response)
        self.assertFalse(response.json['ok'])
        self._check_is_opened()

    def _check_is_opened(self):
        """Проверить, что профиль открыт"""

        profile = Profile.objects.get(id=self._profile.id)
        self.assertFalse(profile.is_closed)
        self.assertTrue(profile.user.is_active)

    def _check_is_closed(self):
        """Проверить, что профиль закрыт"""

        profile = Profile.objects.get(id=self._profile.id)
        self.assertTrue(profile.is_closed)
        self.assertFalse(profile.user.is_active)
