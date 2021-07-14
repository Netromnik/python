# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import logging
from logging.handlers import BufferingHandler

from irk.afisha import permissions as afisha_permissions
from irk.utils.notifications import tpl_notify


def correct_night_session(timestamp):
    """
    :type timestamp: datetime.datetime
    """

    if timestamp.time() <= datetime.time(6, 0):
        return timestamp - datetime.timedelta(days=1)

    return timestamp


def create_afisha_import_logger(name):
    """Логер импорта афишы"""

    log = logging.getLogger('afisha.tickets.import.{}'.format(name))
    handler = BufferingNotificationHandler(1000, name)
    log.setLevel(logging.INFO)
    log.addHandler(handler)
    return log


class BufferingNotificationHandler(BufferingHandler):
    def __init__(self, capacity, name):
        super(BufferingNotificationHandler, self).__init__(capacity)
        self.name = name

    def flush(self):
        if self.buffer:
            items = []
            for record in self.buffer:
                items.append(self.format(record))
            tpl_notify(
                u'Уведомление об импортре с {} '.format(self.name),
                'afisha/notif/import.html',
                {'name': self.name, 'items': items},
                None,
                afisha_permissions.get_moderators().values_list('email', flat=True)
            )
            super(BufferingNotificationHandler, self).flush()
