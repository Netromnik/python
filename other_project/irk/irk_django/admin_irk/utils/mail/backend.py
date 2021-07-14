# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import smtplib

from django.core.mail.backends.smtp import EmailBackend

connection_cache = {'connection': None}

class KeepConnectionEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        super(KeepConnectionEmailBackend, self).__init__(*args, **kwargs)

        if connection_cache['connection']:
            self.connection = connection_cache['connection']


    def open(self):
        status = super(KeepConnectionEmailBackend, self).open()

        if status:
            connection_cache['connection'] = self.connection
        return status


    def close(self):
        if connection_cache['connection']:
            return

        super(KeepConnectionEmailBackend, self).close()


    def send_messages(self, *args, **kwargs):
        try:
            return super(KeepConnectionEmailBackend, self).send_messages(*args, **kwargs)
        except smtplib.SMTPException:
            self.connection = False
            self.open()
            return super(KeepConnectionEmailBackend, self).send_messages(*args, **kwargs)
