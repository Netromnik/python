# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re

from django.core.management.base import BaseCommand

from irk.profiles.models import User


EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


class Command(BaseCommand):
    """
    Массовая отписка пользователей от рассылки

    Скрипт используется для очистки мертвых адресов из списка подписчиков. Адреса
    берутся из файла. Одна строка в файле - один емейл.
    """

    help = 'Массовая отписка пользователей от рассылки'

    def add_arguments(self, parser):
        parser.add_argument('file', help='Файл со списком адресов', type=str)

    def handle(self, *args, **options):
        self.stdout.write('Starting profiles_unsubscribe command')

        emails = self.get_emails(options['file'])
        self.stdout.write('Processing {} emails ...'.format(len(emails)))

        query = User.objects.filter(email__in=emails)
        processed = 0
        unsubs = 0
        for user in query:
            self.stdout.write('unsubscribing id={} email={}  '.format(user.id, user.email), ending='')
            try:
                if user.profile.subscribe:
                    user.profile.subscribe = False
                    user.profile.save()
                    self.stdout.write(self.style.SUCCESS('OK'))
                    unsubs += 1
                else:
                    pass
                    # self.stdout.write(self.style.NOTICE('NOT SUBSCRIBED'))
                processed += 1
            except Exception as err:
                self.stderr.write(str(err))

        self.stdout.write('{} processed, {} unsubscribed'.format(processed, unsubs))
        self.stdout.write('Finished')


    def get_emails(self, path):
        emails = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                m = re.search(EMAIL_REGEX, line, re.IGNORECASE)
                if m:
                    email = m.group(0).lower()
                    if '@gmail.com' in email:  # хотя бы gmail пока
                        emails.append(email)
                elif line and not m:
                    self.stderr.write('No emails: {}'.format(line))

        return emails
