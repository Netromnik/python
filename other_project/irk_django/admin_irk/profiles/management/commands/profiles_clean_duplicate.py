# -*- coding: utf-8 -*-

import uuid

from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, **options):
        fake_email_domain = 'deleted.user.example.org'
        ordering = "-last_login"

        cursor = connection.cursor()

        cursor.execute("""SELECT email, COUNT(*) as cnt
            FROM auth_user
            WHERE email != ''
            GROUP BY email
            ORDER BY cnt DESC""")

        emails = filter(lambda e: e[1] > 1, cursor.fetchall())
        for email, cnt in emails:
            print "**** Duplicated email %s  = %s" % (email, cnt)  # TODO: logging
            users = User.objects.filter(email=email).order_by(ordering)
            for user in users[1:]:
                rnd_hash = str(uuid.uuid4())[:8]
                user.email = '%s@%s' % (rnd_hash, fake_email_domain)
                print '\t', user.email
                user.last_login = user.date_joined
                user.save()
