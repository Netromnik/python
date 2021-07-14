# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import smtplib

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import smart_str

from utils.tasks import email_send

logger = logging.getLogger(__name__)


def notify(title, message, emails=(), sender=None, attachments=None):
    """Отправка E-mail сообщения пользователям

    Параметры:
        title - заголовок письма
        message - текст письма
        emails - список адресатов
        sender - отправитель
    """

    headers = {'From': settings.EMAIL_FROM, 'Reply-To': settings.EMAIL_REPLY_TO}

    if sender:
        headers['From'] = smart_str(sender)

    # Заголовок не должен содержать переносов строк
    title = title.replace('\n', '')

    emails = [email for email in emails if email.strip()]

    if not hasattr(settings, 'DEBUG_MAIL') or not settings.DEBUG_MAIL or settings.EMAIL_HOST == 'localhost':
        try:
            email_send.delay(title, message, emails, headers, attachments)
            # Перехватываем вообще все исключения, здесь это обосновано
        except Exception:
            logger.exception('can not send email via Celery')
        else:
            logger.debug('email added to the task queue: %s %s', emails, title)


def tpl_notify(title, template, context, request=None, emails=(), sender=None, attachments=None):
    """Отправка E-mail сообщения пользователям

    Сообщение рендерится из шаблона"""

    context['ban_periods'] = settings.BAN_PERIODS
    if request:
        msg = render_to_string(template, context, request=request)
    else:
        msg = render_to_string(template, context)

    return notify(title, msg, emails, sender=sender, attachments=attachments)
