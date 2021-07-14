# -*- coding: utf-8 -*-

import datetime

from django.core.management.base import BaseCommand
from django.db import connection

from irk.afisha.models import Period, CurrentSession
from irk.utils.helpers import time_combine


class Command(BaseCommand):
    """ Очистки таблицы кэша афиши с денормализованными данными

        - удаляет все устаревшие данные
        - может обновлять данные
    """

    def add_arguments(self, parser):
        parser.add_argument('--rebuild',
                            action='store_true',
                            dest='rebuild',
                            help='Rebulid table content',
                            default=False)

    def handle(self, *args, **options):
        if options.get('rebuild'):
            self.update()
        else:
            limit = datetime.datetime.now() - datetime.timedelta(1)
            filters = {
                'real_date__lte': limit,
                'kassysession__isnull': True,
                'ramblersession__isnull': True,
                'kinomaxsession__isnull': True,
            }
            CurrentSession.objects.filter(**filters).delete()

    def update(self):
        """ Обновление данных таблицы  """

        curr = connection.cursor()
        curr.execute('DELETE FROM %s' % CurrentSession._meta.db_table)

        now = datetime.date.today()  # TODO: переименовать в `today`
        periods = Period.objects.filter(end_date__gte=now).select_related('event_guide', 'event_guide__event')

        for period in periods:
            if period.event_guide.event.is_hidden:
                continue

            current_date = period.start_date if period.start_date >= now else now
            limit_date = period.end_date  # if period.end_date <= limit else limit
            sessions = list(period.sessions_set.all())

            while current_date <= limit_date:
                if sessions:
                    for session in sessions:
                        real_date = datetime.datetime.combine(current_date, session.time)
                        if session.time <= datetime.time(6, 0):
                            real_date += datetime.timedelta(1)

                        CurrentSession.objects.create(
                            date=current_date,
                            time=session.time,
                            filter_time=session.time,
                            fake_date=datetime.datetime.combine(current_date, session.time),
                            real_date=real_date,
                            end_date=time_combine(real_date, period.duration),
                            event_type=period.event_guide.event.type,
                            event_guide=period.event_guide,
                            guide_id=period.event_guide.guide_id,
                            event_id=period.event_guide.event_id,
                            is_hidden=period.event_guide.event.is_hidden,
                            period=period,
                            hall=period.event_guide.hall,
                            is_3d=period.is_3d,
                        )

                else:
                    # Если у периода нет сеансов, значит уточняется расписание
                    real_date = datetime.datetime.combine(current_date, datetime.time(23, 59, 59))
                    CurrentSession.objects.create(
                        date=current_date,
                        time=None,
                        filter_time=None,
                        fake_date=datetime.datetime.combine(current_date, datetime.time(0, 0, 0)),
                        real_date=real_date,
                        end_date=time_combine(real_date, period.duration),
                        event_type=period.event_guide.event.type,
                        event_guide=period.event_guide,
                        guide_id=period.event_guide.guide_id,
                        event_id=period.event_guide.event_id,
                        is_hidden=period.event_guide.event.is_hidden,
                        period=period,
                        hall=period.event_guide.hall,
                        is_3d=period.is_3d,
                    )
                current_date += datetime.timedelta(1)
