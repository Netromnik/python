# -*- coding: utf-8 -*-

import datetime

from django.core.management.base import BaseCommand
from django.db import connection
from reversion.models import Revision
from irk.utils.helpers import yes_or_no


class Command(BaseCommand):
    """
    Удаляет записи таблицы reversion_version старше определенного срока.
    Перед запуском следует забэкапить и сохранить таблицу reversion_version для истории.
    """

    def handle(self, *args, **options):
        if yes_or_no('Did you backup the table "reversion_version"?'):
            days = 30

            start_date = datetime.datetime.today() - datetime.timedelta(days=days)

            revision = Revision.objects.filter(date_created__gte=start_date).order_by('date_created').first()

            sql = 'DELETE FROM reversion_version WHERE revision_id<{}'.format(revision.pk)

            cursor = connection.cursor()
            cursor.execute(sql)

            print('Done')
