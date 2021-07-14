# coding=utf-8
from __future__ import absolute_import, print_function, unicode_literals

import datetime
import email
import logging
import poplib

from django.core.management.base import BaseCommand

from irk.utils.bounce import BounceRegistrator, BounceUnsubscriber
from irk.utils.helpers import parse_email_date

log = logging.getLogger(__name__)

DELETE_MESSAGES_OLDER = 30  # days


class Command(BaseCommand):
    """
    Импорт и регистрация недоставленных писем

    Соединяется с ящиком, куда приходят баунсы, и забирает оттуда всю почту.
    Каждое письмо проверяется. Если это на самом деле баунс, он регистрируется
    в базе данных, а письмо из ящика удаляется.

    В ящике остаются нераспознанные письма. Можно при необходимости доработать
    алгоритм и запустить команду повторно.
    """

    help = 'Импорт и регистрация недоставленных писем'

    def handle(self, *args, **options):
        log.info('Starting profiles_process_bounces command')

        too_old = datetime.datetime.now() - datetime.timedelta(days=DELETE_MESSAGES_OLDER)

        registrator = BounceRegistrator()
        processed = 0
        deleted = 0

        mailbox = BounceMailbox()

        with mailbox:
            for msgid, text in mailbox.fetch_messages():
                # получим письма из ящика и сохраним как события в базе данных
                msg = email.message_from_string(text)
                log.info('processing message %s %s', msg['Date'], msg['Subject'])

                registered = registrator.register(msg, hash(text))
                if registered:
                    # сохранено в базе, удалим из ящика
                    log.debug('deleting email')
                    mailbox.delete_message(msgid)
                    deleted += 1
                else:
                    if msg['Date']:
                        msg_date = parse_email_date(msg['Date'])
                        # удаляем все старые письма без разбора
                        if msg_date < too_old:
                            log.debug('message is not processed, but its too old, I will delete it now')
                            mailbox.delete_message(msgid)
                            deleted += 1
                            continue

                    log.debug('message is not processed, I will not delete it')

                processed += 1

        # сразу и очистку запустим
        b = BounceUnsubscriber()
        b.run()

        log.info('Done. %d processed, %d deleted', processed, deleted)


class BounceMailbox(object):
    """
    Коннектор к почтовому ящику
    Устанавливает соединение при вызове через `with`
    Этот замечательный пример класса контекстного менеджера я нашел в книге
    Python Cookbook, 3rd editoin, глава 8.3 (советую)
    """
    def __init__(self):
        self.host = 'relay.baik.ru'
        self.user = 'mailer@baik.ru'
        self.passwd = '1spamergotohell!'
        self.conn = None

    def __enter__(self):
        if self.conn is not None:
            raise RuntimeError('Already connected')

        self.conn = poplib.POP3(self.host)
        self.conn.user(self.user)
        self.conn.pass_(self.passwd)

        return self.conn

    def __exit__(self, exc_ty, exc_val, tb):
        self.conn.quit()
        self.conn = None

    def fetch_messages(self):
        if self.conn is None:
            raise RuntimeError('Please call me inside `with` statement')

        _, messages, _ = self.conn.list()
        log.info('Found %d news messages', len(messages))

        for item in messages:
            msgid, length = item.split(' ')

            log.debug('fetching message %s, %s bytes', msgid, length)
            _, lines, _ = self.conn.retr(msgid)

            # тело письма приходит как массив строк, преобразуем в одну
            yield msgid, b'\n'.join(lines)

    def delete_message(self, msgid):
        if self.conn is None:
            raise RuntimeError('Please call me inside `with` statement')

        self.conn.dele(msgid)
