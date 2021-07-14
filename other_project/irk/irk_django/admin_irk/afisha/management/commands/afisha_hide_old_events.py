# -*- coding: utf-8 -*-

import datetime

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """ Скрытие событий """

    def handle(self, *args, **options):
        # Скрытие событий последний период которых закончился позавчера
        sql = """UPDATE afisha_event SET is_hidden = TRUE WHERE id in (
                    SELECT id FROM (
                        SELECT ae.id, ae.title, ae.is_hidden, MAX(ap.end_date) AS end_date
                        FROM afisha_event AS ae
                        INNER JOIN afisha_eventguide AS aeg ON ae.id = aeg.event_id
                        INNER JOIN afisha_period AS ap ON aeg.id = ap.event_guide_id
                        INNER JOIN afisha_sections AS ase ON ase.id = ae.type_id
                        WHERE ase.hide_past = TRUE
                        GROUP BY ae.id
                        HAVING end_date < '%s' AND ae.is_hidden = FALSE
                        ORDER BY end_date DESC
                    ) AS ids
                )""" % (datetime.date.today() - datetime.timedelta(1))

        cursor = connection.cursor()
        cursor.execute(sql)

        # Скрытие событий не привязанных к гиду
        sql = """UPDATE afisha_event SET is_hidden = TRUE WHERE id in (
                    SELECT id FROM (
                        SELECT ae.id
                        FROM afisha_event AS ae
                        LEFT JOIN afisha_eventguide AS aeg ON ae.id = aeg.event_id
                        WHERE aeg.event_id IS NULL
                    ) AS ids
                 )"""

        cursor = connection.cursor()
        cursor.execute(sql)

        call_command('elasticsearch', 'afisha.Event', remap=True)  # Пересчитываем поиск
