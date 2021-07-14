# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import urlparse

from django.contrib.contenttypes.models import ContentType

from irk.utils.db.kv import get_redis
from irk.utils.helpers import get_client_ip


def content_type_for_comments(obj):
    """Returns actual content type for the object when need add comments"""

    from irk.news.models import BaseMaterial
    from irk.phones.models import Firms

    if isinstance(obj, BaseMaterial):
        return ContentType.objects.get_for_model(BaseMaterial)
    elif isinstance(obj, Firms):
        return ContentType.objects.get_for_model(Firms)
    else:
        return ContentType.objects.get_for_model(obj)


def delete_spam_comment(comment, pattern, logger):
    """Хелпер для удаления сообщения при проверке на спам"""

    from irk.comments.models import Comment

    comment.status = Comment.STATUS_SPAM
    comment.save()

    logger.info('Message #%s considered as spam with pattern "%s"' % (comment.id, pattern))


class CommentSpamChecker(object):
    """
    Проверка комментария на спам
    """

    # Список разрешенных доменов
    allowed_hosts = ['irk.ru', 'diffrent.ru', 'youtu.be', 'youtube.com', 'instagram.com', 'vk.com', 'fb.com',
                     'twitter.com', 'ok.ru']
    # Разрешенное количество дней прошедших после регистрации
    old_profile_days = 1
    # Разрешенное количество дней прошедших c момента поста видимого комментария
    visible_comments_days = 1
    # Время в течение которого повторный пост сообщения с той же ссылкой считается слишком частым
    comment_link_too_often_time = 60 * 30
    # Время в течение которого повторный пост любого сообщения с ссылкой считается слишком частым
    comment_post_too_often_time = 20
    # Время хранения забанненых ссылок
    ban_link_time = 60 * 60 * 24 * 30

    banned_link_key = 'comments.bannedlink'
    user_link_key = 'comments.userlink'
    user_post_key = 'comments.userpost'

    def __init__(self, request, text):
        self.user = request.user
        self.text = text
        self.ip = get_client_ip(request)
        self.now = datetime.datetime.now()

    def is_contain_link(self):
        """
        Проверка текста на наличие ссылок
        """
        if 'http://' in self.text or 'https://' in self.text or 'www.' in self.text:
            return True
        return False

    def is_user_suspicious(self):
        """
        Проверка аккаунта на подозрительность
        """

        from irk.comments.models import Comment

        # Сотрудники вне подозрения
        if self.user.is_staff:
            return False

        # Пользователь зарегистрирован давно
        is_old_user = self.user.date_joined + datetime.timedelta(self.old_profile_days) < self.now

        # Есть нормальные комментарии
        has_normal_comment = Comment.objects.filter(
            user_id=self.user.pk, created__lte=self.now - datetime.timedelta(self.visible_comments_days)) \
            .visible().exists()

        if is_old_user and has_normal_comment:
            return False
        return True

    def is_ip_banned(self):
        """
        Проверка IP на забаненность
        """

        from irk.comments.models import SpamIp

        if SpamIp.objects.filter(ip=self.ip).exists():
            return True
        return False

    def is_link_banned(self, url):
        """
        Проверка ссылки на забаненность
        """

        redis = get_redis()

        result = redis.get('{}.{}'.format(self.banned_link_key, url))
        if result is None:
            return False
        return True

    def is_link_allowed(self, url):
        """
        Проверка ссылки в по белому листу
        """
        url_parsed = urlparse.urlparse(url)
        location = url_parsed.netloc.replace('www.', '')
        if location in self.allowed_hosts:
            return True
        return False

    def is_too_often_link(self, url):
        """
        Было ли недавно добавлено этим же юзером сообщение с такой же ссылкой
        """
        redis = get_redis()
        result = redis.get('{}.{}.{}'.format(self.user_link_key, self.user.pk, url))

        if result is None:
            return False
        return True

    def is_too_often_post(self):
        """
        Постит ли пользователь сообщения с ссылками слишком часто
        """
        redis = get_redis()
        result = redis.get('{}.{}'.format(self.user_post_key, self.user.pk))

        if result is None:
            return False
        return True

    def set_often_link(self, url):
        """
        Сохранить время публикации комментария с ссылкой пользователем
        """
        redis = get_redis()
        redis.setex('{}.{}.{}'.format(self.user_link_key, self.user.pk, url), self.comment_link_too_often_time, '')

    def set_often_post(self):
        """
        Сохранить время публикации последнего комментария с ссылкой пользователем
        """
        redis = get_redis()
        redis.setex('{}.{}'.format(self.user_post_key, self.user.pk), self.comment_post_too_often_time, '')

    def ban_link(self, url):
        """
        Забанить ссылку
        """
        redis = get_redis()
        redis.setex('{}.{}'.format(self.banned_link_key, url), self.ban_link_time, '')

    def check(self):
        """
        Выполнить проверку на спам
        """

        from irk.utils.text.formatters.bb import url_re

        if self.is_contain_link() and self.is_user_suspicious():

            if self.is_ip_banned():
                self.do_ban('IP забанен')
                return True

            urls = url_re.findall(self.text)

            for i, url in enumerate(urls):
                if self.is_link_allowed(url):
                    continue

                if self.is_link_banned(url):
                    self.do_ban('Ссылка забанена', url)
                    return True

                if self.is_too_often_link(url):
                    self.do_ban('Слишком частый пост ссылки', url)
                    return True

                self.set_often_link(url)

            if self.is_too_often_post():
                self.do_ban('Слишком частый пост сообщений с сылками', url)
                return True

            self.set_often_post()

        return False

    def do_ban(self, reason, url=None):
        """
        Бан
        """

        from irk.comments.models import SpamIp, SpamLog
        from irk.profiles.controllers import BanController

        # Бан IP
        SpamIp.objects.get_or_create(ip=self.ip)

        # Бан пользователя
        controller = BanController()
        controller.ban(self.user, reason='Спам')
        controller.delete_all_user_messages(self.user)

        # Бан ссылки
        if url:
            self.ban_link(url)

        # Сохранение лога
        SpamLog(user=self.user, text=self.text, ip=self.ip, reason=reason).save()
