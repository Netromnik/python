# -*- coding: utf-8 -*-

import datetime
import ephem
import logging
from itertools import chain

from django.core.management.base import BaseCommand, CommandError

from irk.weather.models import MoonTiming

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<year>'
    help = u'Расчитать лунные дни на год'

    def __init__(self):
        super(Command, self).__init__()

        self._irk = ephem.Observer()
        self._irk.lon, self._irk.lat = '104:18:18.1', '52:17:13.1'
        self._moon = ephem.Moon()

    def handle(self, *args, **options):
        logger.debug('Start calculate moon days')

        if len(args) == 1:
            self.year = int(args[0])
        else:
            self.year = datetime.date.today().year

        start_date = ephem.Date(datetime.datetime(self.year, 1, 1, 0, 0))
        end_date = ephem.Date(datetime.datetime(self.year + 1, 1, 1, 0, 0))

        new_moons = self._get_new_moons(start_date, end_date)
        moon_rises = self._get_moon_rises(new_moons[0]['start'], end_date)

        # Новолуния и восходы объединяются в один список. Каждое новолуние это начало лунного месяца, т.е. начинается
        # первый лунный день. Все восходы луны до следующего новолуния обозначают начало нового лунного дня.
        data = sorted(chain(new_moons, moon_rises), key=lambda x: x['start'])
        data = self._prepare(data)
        self._update_moon_timings(data)

        logger.debug('Finish calculate moon days')

    def _get_new_moons(self, start_date, end_date):
        """Получить новолуния"""

        new_moons = []
        current_date = ephem.previous_new_moon(start_date)
        while current_date < end_date:
            new_moons.append({'type': 'new', 'start': current_date})
            current_date = ephem.next_new_moon(current_date)

        return new_moons

    def _get_moon_rises(self, start_date, end_date):
        """Получить восходы луны"""

        rises = []
        current_date = start_date
        counter = 0
        while current_date < end_date:
            self._irk.date = ephem.date(start_date + counter)
            self._moon.compute(self._irk)
            current_date = self._moon.rise_time
            if current_date:
                rises.append({'type': 'rise', 'start': current_date})
            counter += 1

        return rises

    def _prepare(self, data):
        """Подготовить данные для сохранения"""

        # Удаляем восходы до первого известного новолуния
        for i, row in enumerate(data[:]):
            if row['type'] == 'new':
                break
            del data[i]

        result = []
        counter = 0
        for i, row in enumerate(data):
            try:
                next_row = data[i+1]
            except IndexError:
                # Если нет следуещего элемента, то просто пропускаем данную строку
                continue

            if row['type'] == 'new':
                counter = 1
            else:
                counter += 1

            result.append({
                'number': counter,
                'start': row['start'],
                'end': next_row['start'],
            })

        return result

    def _update_moon_timings(self, data):
        """Обновить график лунных дней"""

        MoonTiming.objects.filter(start_date__year=self.year).delete()

        for row in data:
            start_date = ephem.localtime(row['start'])
            end_date = ephem.localtime(row['end'])
            if start_date.year != self.year:
                continue

            MoonTiming.objects.create(number=row['number'], start_date=start_date, end_date=end_date)
