# coding=utf-8
"""Обработчик баунс-сообщений электронной почты

Не все письма доходят. Со временем подписанные пользователи теряются и их ящики
забиваются или перестают работать. Таких людей нужно отписывать от рассылки новостей
и уведомлений, чтобы не загрузать почтовую систему и чтобы нас не считали спамерами.

При недоставленном письме к нам на адрес settings.EMAIL_SMTP_FROM придет баунс-письмо.
Мы забираем письмо скриптом news_get_bounces, и сохраняем событие в базе данных.
Письма, которые не являются баунсами или которые невозможно понять, удаляются,
не регистрируя события.

Потом отдельный класс просматривает таблицу и отписывает всех, кто не получил почту
три дня в течение семи дней.

Этот модуль вдохновлен mailmain: https://www.aosabook.org/en/mailman.html
"""

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import logging
import re

from django.db.models import Count, Max

from irk.profiles.models import BounceEvent, User
from irk.utils.helpers import parse_email_date

log = logging.getLogger(__name__)

# если на пользователя за последние BOUNCE_INTERVAL дней приходилось BOUNCE_SCORE дней,
# в которое было хоть одно баунс-письмо, то мы его отписываем
BOUNCE_SCORE = 3
BOUNCE_INTERVAL = 7

DELAYED_PATTERN = re.compile(r'warning: message .+ delayed \d+ hours', re.IGNORECASE)


class BounceRegistrator(object):
    """
    Обрабочик баунсов добавляет их в базу, классифицирует
    """

    def register(self, msg, msghash=None):
        """
        Парсит письмо и добавляет событие в базу

            msg - объект email.Message
            msghash - используется, чтобы избежать дублирования в базе данных

        Возвращает True, если письмо обработано и его можно удалить из почтового ящика
        """

        DELETE = True
        DONT_DELETE = False

        pipeline = [
            self._skip_moderators,
            self._skip_autoreply,
            self._skip_long_lines,
            self._skip_delayed,
            self._find_recipient,
            self._link_user,
            self._fill_details,
            self._skip_spam_rejects,
        ]

        # run pipeline and fill meta
        meta = {}
        for func in pipeline:
            try:
                func(msg, meta)
            except SkipMessageDontDelete:
                log.debug('message skipped, let it be')
                return DONT_DELETE
            except SkipMessage:
                log.debug('message skipped')
                return DELETE
            except Exception:  # pylint: disable=broad-except
                log.exception('error in message parsing')
                return DONT_DELETE

        # раз дошли сюда, сообщение надо регистрировать
        if msghash:
            event, created = BounceEvent.objects.get_or_create(hash=msghash)
        else:
            event = BounceEvent()

        event.email = meta.get('recipient', '')
        event.details = meta.get('details', '')
        event.message_date = meta.get('message_date')
        event.date = event.message_date.date() if event.message_date else None
        event.message_id = meta.get('message_id', '')
        event.user = meta.get('user')
        event.save()

        log.debug('Event saved')

        return DELETE

    @staticmethod
    def _skip_autoreply(msg, meta):
        if 'X-AutoReply' in msg:
            log.debug('This is autoreply for %s, skipping', msg['X-AutoReply'])
            raise SkipMessage('autoreply')

    @staticmethod
    def _skip_moderators(msg, meta):
        """
        Отсекать письма модераторам

        Поскольку модераторов не нужно отписывать от рассылки, то обработка цепочки прекращается.
        """
        if 'X-Failed-Recipients' in msg:
            recipients = msg['X-Failed-Recipients'].replace('\n', '').strip()
            # только модераторы получают письма с несколькими адресатами
            if ',' in recipients:
                log.debug('Skipping moderators')
                raise SkipMessage('moderator')

    @staticmethod
    def _skip_long_lines(msg, meta):
        """
        Отсекать письма про ошибку длинной строки SMTP

        Это не проблема адресата, это мы неправильно письмо закодировали перед отправкой.
        """

        if b'maximum allowed line length' in bytes(msg):
            log.debug('Skipping 998 octets error message. Fix your emails!')
            raise SkipMessage('long lines')

    @staticmethod
    def _find_recipient(msg, meta):
        """
        Кому было адресовано недошедшее письмо?
        """
        if 'X-Failed-Recipients' in msg:
            meta['recipient'] = msg['X-Failed-Recipients'].replace('\n', '').strip().lower()
            log.debug('Found recipient: %s', meta['recipient'])
        else:
            # надо будет придумать способ определять больше получателей
            log.warning('No x-failed-recipients %s %s', msg['Date'], msg['Message-id'])

            # пусть письмо на сервере останется, может потом распознаем
            raise SkipMessageDontDelete()

    @staticmethod
    def _link_user(msg, meta):
        """
        Находит нашего пользователя по емейлу
        """
        if meta['recipient']:
            try:
                user = User.objects.get(email=meta['recipient'])
            except User.DoesNotExist:
                # нет такого юзера, удалим письмо
                log.warning('Can not find user with email "%s"', meta['recipient'])
                raise SkipMessage('no such user')

            meta['user'] = user

    @staticmethod
    def _fill_details(msg, meta):
        if 'Date' in msg:
            meta['message_date'] = parse_email_date(msg['Date'])

        if 'Message-Id' in msg:
            meta['message_id'] = msg['Message-Id']

        meta['details'] = ''
        if msg.is_multipart():
            for part in msg.get_payload():
                # как правило, в текстовой части полезная инфа про причину недоставки
                if 'text/plain' in part.get('Content-type', '').strip():
                    meta['details'] += part.get_payload() + b'\n'
        else:
            meta['details'] = msg.get_payload()

    @staticmethod
    def _skip_spam_rejects(msg, meta):
        # Наш айпишник могли забанить в каком-то почтовом сервисе. В этом случае
        # никакая почта доходить не будет - пользователи тут ни при чем
        if meta['details']:
            if b'reduce the amount of spam sent to Gmail' in meta['details']:
                log.warning('Gmail banned our message, AHTUNG!!!')
                raise SkipMessage('gmail ban')
            if b'550 spam message rejected' in meta['details']:
                log.warning('Mail.ru banned our message, AHTUNG')
                raise SkipMessage('mailru ban')

    @staticmethod
    def _skip_delayed(msg, meta):
        # Warning: message 1j7I9V-0000Dm-Ow delayed 72 hours - просто удалим
        if DELAYED_PATTERN.match(msg['subject']):
            raise SkipMessage('delay message')


class BounceUnsubscriber(object):
    """
    Отписывает людей, у которых слишком много баунсов.

    Считает количество дней, которые человек получал баунсы. Можно было бы считать
    просто количество писем, но может быть, что два дня почта не работала, а на третий
    заработала. А если три дня не работает - то скорее всего быстро проблема не решится
    и тогда мы отписываем человека.
    """
    def run(self):
        log.info('Unsubscribing emails with too many bounces')
        log.info('Limit: %d bounce days in last %d days interval', BOUNCE_SCORE, BOUNCE_INTERVAL)

        lookup_interval = self._get_interval()

        # если у пользователя было за последнюю неделю больше трех дней, когда
        # ему приходили баунсы, то он попадет в эту выборку
        query = BounceEvent.objects \
            .values_list('email') \
            .filter(date__gt=lookup_interval) \
            .annotate(unique_days=Count('date', distinct=True), last_bounce_id=Max('id')) \
            .filter(unique_days__gte=BOUNCE_SCORE)

        unsubscribed = 0

        for email, days, last_bounce_id in query:
            log.info('%s reached limit having %d bounce days', email, days)

            user = BounceEvent.objects.get(id=last_bounce_id).user
            log.debug('user id is %d', user.id)

            user.profile.subscribe = False
            user.profile.comments_notify = False
            user.profile.save(update_fields=['subscribe', 'comments_notify'])

            unsubscribed += 1

        log.info('Done. Total unsubscribed is %d', unsubscribed)

    def _get_interval(self):
        return datetime.date.today() - datetime.timedelta(days=BOUNCE_INTERVAL)


class SkipMessage(Exception): pass
class SkipMessageDontDelete(SkipMessage): pass
