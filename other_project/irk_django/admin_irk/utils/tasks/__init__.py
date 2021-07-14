# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging
import smtplib
import random
import requests

from django.conf import settings
from django.core.mail import get_connection, EmailMessage

from utils.tasks.helpers import task
from utils.exceptions import raven_capture

logger = logging.getLogger(__name__)

SAID = '''\
бросил буркнул вздохнул возмутился возразил воскликнул восхитился
выговорил добавил доложил заверил завопил закричал заметил
запротестовал засмеялся заявил изумился кивнул крикнул настаивал
начал объявил оживился осведомился ответил отозвался перебил
повторил подтвердил поправил попросил посоветовал
пояснил предложил предположил представил пригласил признался пробормотал
пробурчал провозгласил проворчал проговорил продолжал произнес промолвил
промычал протянул процедил прошептал прояснил парировал размышлял
рассердился согласился сообщил спохватился спросил убеждал удивился
улыбнулся успокоил уточнил'''.split()


@task(default_retry_delay=10, ignore_result=True)
def email_send(title, message, emails, headers, attachments):
    """Задача отправки письма

    При проблемах с отправкой, начинает пробовать отправиться заново
    с интервалом в 10 секунд"""

    email = EmailMessage(title, message, settings.EMAIL_SMTP_FROM,
                         emails, headers=headers, attachments=attachments)
    email.encoding = 'utf-8'
    email.content_subtype = 'html'

    kwargs = {'fail_silently': False}

    try:
        with get_connection(**kwargs) as connection:
            connection.send_messages([email])
    except smtplib.SMTPServerDisconnected as e:
        # Если сервер неожиданно разорвал соединение, пробуем отправить заново
        email_send.retry(exc=e)
    except smtplib.SMTPResponseException as e:
        # При всех проблемах с отправкой писем не пытаемся больше отправить письмо
        # TODO: логгирование ошибок
        logger.exception('Can not send email')
        raven_capture()
        return


@task(default_retry_delay=10)
def send_discord_mistype(context):
    context['said'] = random.choice(SAID)
    if not context['user_authenticated']:
        tpl = '\n<{url}>\n```markdown\n# {text}\n\n{description}```\n— {said} анонимный пользователь\n\n'
        data = {
            'content': tpl.format(**context),
        }
    else:
        tpl = '\n<{url}>\n```markdown\n# {text}\n\n{description}```\n— {said} {user_name} <{user_link}>\n\n'
        data = {
            'content': tpl.format(**context),
        }

    DISCORD_MISTYPES_HOOK = 'https://discordapp.com/api/webhooks/428029950222925836/HEkf_5cIE7vuALbgvbWoGcH1jPwCoyZahz64BxZJmUPaeQ5DGBBitDAcbPeZbeQ87pB7'
    res = requests.post(DISCORD_MISTYPES_HOOK, json=data)
    res.raise_for_status()
