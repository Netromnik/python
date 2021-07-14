# -*- coding: utf-8 -*-

import datetime

from irk.comments.models import Comment, ActionLog
from irk.comments.tasks import delete_all_user_comments
from irk.profiles.models import UserBanHistory
from irk.utils.helpers import get_object_or_none


class BanController(object):
    """Контроллер для блокировки/разблокировки пользователей"""

    def __init__(self, moderator=None):
        """
        :param moderator: модератор
        """

        self._moderator = moderator

    def ban(self, user, **kwargs):
        """Забанить пользователя"""

        user.profile.is_banned = True

        now = datetime.datetime.now()
        period = kwargs.get('period')
        ban_end = now + datetime.timedelta(period) if period else None

        user.profile.bann_end = ban_end

        if not user.profile.hash_stamp:
            user.profile.hash_stamp = now

        user.profile.save()

        reason = kwargs.get('reason', '').strip()
        UserBanHistory.objects.create(
            moderator=self._moderator, user=user, reason=reason, created=now, ended=ban_end
        )

    def unban(self, user):
        """Разблокировать пользователя. Сообщения нужно восстанавливать вручную."""

        user.profile.is_banned = False
        user.profile.bann_end = None
        user.profile.save()

    def delete_message(self, comment_id):
        """Удалить сообщение"""

        comment = get_object_or_none(Comment, pk=comment_id)
        if not comment:
            return

        comment.status = Comment.STATUS_DIRECT_DELETE
        comment.save()
        ActionLog.objects.create(action=ActionLog.ACTION_DELETE, comment=comment, user=self._moderator)

    def delete_all_user_messages(self, user):
        """Удалить все сообщения пользователя"""

        moderator_id = self._moderator.pk if self._moderator else None

        delete_all_user_comments.delay(user.pk, moderator_id)
