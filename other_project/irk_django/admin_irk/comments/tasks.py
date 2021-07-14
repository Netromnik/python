# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import logging

from django.contrib.auth.models import User
from django.utils.html import word_split_re, WRAPPING_PUNCTUATION

from irk.comments.helpers import delete_spam_comment
from irk.comments.models import Comment, ActionLog, SpamPattern
from irk.utils.grabber import proxy_requests
from irk.utils.tasks.helpers import task
from irk.utils.text.formatters.bb import url_re

TRAILING_PUNCTUATION = ['.', ',', ':', ';', '.)', '"', '\'', '!']


@task(ignore_result=True)
def spam_check(comment_id):
    """ Проверка сообщения форума на наличие паттернов, соответствующих спаму. Перенесено из форума.
    """

    logger = logging.getLogger(__name__)

    comment = Comment.objects.get(pk=comment_id)
    text = comment.text.lower()

    patterns = [x.lower() for x in SpamPattern.objects.all().values_list('text', flat=True)]

    # Сначала просто проверяем текст сообщения
    for pattern in patterns:
        if pattern in text:
            return delete_spam_comment(comment, pattern, logger)

    # Часть кода взята из django.utils.html.urlize()
    words = word_split_re.split(comment.text)
    for i, word in enumerate(words):
        if '.' in word or '@' in word or ':' in word:
            # Deal with punctuation.
            lead, middle, trail = '', word, ''
            for punctuation in TRAILING_PUNCTUATION:
                if middle.endswith(punctuation):
                    middle = middle[:-len(punctuation)]
                    trail = punctuation + trail
            for opening, closing in WRAPPING_PUNCTUATION:
                if middle.startswith(opening):
                    middle = middle[len(opening):]
                    lead += opening
                    # Keep parentheses at the end only if they're balanced.
                if middle.endswith(closing) and middle.count(closing) == middle.count(opening) + 1:
                    middle = middle[:-len(closing)]
                    trail = closing + trail

            url = None
            if url_re.match(middle):
                url = middle
                if url and not url.startswith('http'):
                    url = 'http://{}'.format(url)

            if url:
                # Запрашиваем указанный URL. `requests` автоматически проходит по всем редиректам, таким образом
                # мы получим конечный URL, если были использованы сокращатели ссылок и прочее.
                try:
                    result_url = proxy_requests.get(url).url.lower()
                except (proxy_requests.InvalidURL, proxy_requests.ConnectionError) as e:
                    logger.warning('Cannot check URL "{0}" for spam. Reason: {1}'.format(url, e))
                    continue

                for pattern in patterns:
                    if pattern in result_url:
                        return delete_spam_comment(comment, pattern, logger)

    logger.info('Message #%s is not considered as spam' % comment.id)


@task(ignore_result=True)
def clear_spam(pattern, stamp=None):
    """Проверка сообщения форума на наличие паттернов, соответствующих спаму. Перенесено из форума."""

    logger = logging.getLogger(__name__)

    if not stamp:
        stamp = datetime.datetime.now() - datetime.timedelta(1)

    comments = Comment.objects.filter(created__gte=stamp).visible()

    for comment in comments:
        if pattern in comment.text.lower():
            delete_spam_comment(comment, pattern, logger)


@task(ignore_result=True)
def delete_all_user_comments(user_id, moderator_id=None):
    """ Удаление всех сообщений пользователя

    Параметры::
        user_id - id пользователя
        moderator_id - id модератора
    """

    user = User.objects.get(pk=user_id)
    moderator = User.objects.get(pk=moderator_id) if moderator_id else None
    comments = Comment.objects.filter(user=user).visible().order_by('-pk')

    # Ради производительности не сохраняем через save чтобы не обновлять кэши
    comments.update(status=Comment.STATUS_SPAM)

    for comment in comments:
        # comment.status = Comment.STATUS_SPAM
        # comment.save()
        ActionLog.objects.create(action=ActionLog.ACTION_DELETE, user=moderator, comment=comment)
