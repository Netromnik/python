# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from irk.comments.models import Comment
from irk.tests.unit_base import UnitTestBase


class BanViewTest(UnitTestBase):
    """Тесты представления бана"""

    csrf_checks = False

    def setUp(self):
        self.moderator = self.create_user('moderator', is_admin=True)
        self.user = self.create_user('user')
        self.comment = G(Comment, user=self.user)
        self.url = reverse('profiles:ban', kwargs={'user_id': self.user.pk})

    def test_action_ban(self):
        """
        Проверка команды Забанить

        Пользователь блокируется, если передан id сообщения, то оно удаляется
        """
        data = {
            'action': 'ban',
            'period': 7,
            'reason': 'fool',
            'message_id': self.comment.pk,
        }

        response = self.ajax_post(self.url, data, user=self.moderator)

        self.assertTrue(response.json['ok'])
        self.assertTrue(User.objects.get(pk=self.user.pk).profile.is_banned)
        self.assertTrue(Comment.objects.get(pk=self.comment.pk).is_deleted)

    def test_action_spam(self):
        """
        Проверка команда Забанить за спам.

        Пользователь блокируется, а все его сообщения помечаются как удаленные
        """
        data = {
            'action': 'spam',
        }

        response = self.ajax_post(self.url, data, user=self.moderator)

        self.assertTrue(response.json['ok'])
        self.assertTrue(User.objects.get(pk=self.user.pk).profile.is_banned)
        # NOTE: проверить удаление всех сообщений не получается, т.к. удаление происходит через celery

    def test_action_unban(self):
        """Проверка команды Снять бан."""

        self.user.profile.is_banned = True
        self.user.profile.save()

        data = {
            'action': 'unban',
        }

        response = self.ajax_post(self.url, data, user=self.moderator)

        self.assertTrue(response.json['ok'])
        self.assertFalse(User.objects.get(pk=self.user.pk).profile.is_banned)

    def test_not_action(self):
        """Команда не указана"""

        data = {
            'period': 7,
            'material_id': self.comment.pk,
        }

        response = self.ajax_post(self.url, data, user=self.moderator)

        self.assertFalse(response.json['ok'])
        self.assertFalse(User.objects.get(pk=self.user.pk).profile.is_banned)

    def test_invalid_action(self):
        """Неверная команда"""

        data = {
            'action': 'unknown',
            'period': 7,
        }

        response = self.ajax_post(self.url, data, user=self.moderator)

        self.assertFalse(response.json['ok'])
        self.assertFalse(User.objects.get(pk=self.user.pk).profile.is_banned)

    def test_invalid_user(self):
        """Неверный идентификатор пользователя"""

        data = {
            'action': 'unban',
        }
        self.user.delete()

        response = self.ajax_post(self.url, data, user=self.moderator)

        self.assertFalse(response.json['ok'])
