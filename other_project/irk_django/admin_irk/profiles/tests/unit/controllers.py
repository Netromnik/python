# -*- coding: utf-8 -*-

import datetime

from django_dynamic_fixture import G

from irk.comments.models import Comment
from irk.tests.unit_base import UnitTestBase

from irk.profiles.controllers import BanController
from irk.profiles.models import Profile


class BanControllerTest(UnitTestBase):
    """Тесты контроллера бана пользователей"""

    def setUp(self):
        self.moderator = self.create_user('admin', is_admin=True)
        self.ctrl = BanController(self.moderator)

    def test_ban_forever(self):
        """Проверка бана навсегда"""

        user = self.create_user('user')
        self.assertFalse(user.profile.is_banned)

        self.ctrl.ban(user)

        self.assertTrue(Profile.objects.get(pk=user.profile.id).is_banned)

    def test_ban_7_days(self):
        """Проверка бана на 7 дней"""

        user = self.create_user('user')
        self.assertFalse(user.profile.is_banned)

        self.ctrl.ban(user, period=7)

        self.assertTrue(Profile.objects.get(pk=user.profile.id).is_banned)
        ban_end = datetime.datetime.now() + datetime.timedelta(7)
        self.assertEqual(ban_end.date(), user.profile.bann_end.date())

    def test_unban(self):
        """Проверка снятия бана"""

        user = self.create_user('user')
        user.profile.is_banned = True
        user.profile.save()

        self.ctrl.unban(user)

        self.assertFalse(Profile.objects.get(pk=user.profile.id).is_banned)

    def test_delete_message(self):
        """Проверка удаления сообщения"""

        message = G(Comment)
        self.assertFalse(message.is_deleted)

        self.ctrl.delete_message(Comment.pk)

        self.assertTrue(Comment.objects.get(pk=message.pk).is_deleted)
