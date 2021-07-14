# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime

from django_dynamic_fixture import G
from freezegun import freeze_time

from irk.map.models import Cities as City
from irk.phones.models import Firms as Firm, Address, Worktime
from irk.tests.unit_base import UnitTestBase


class EveryDayAddressWorktimeTest(UnitTestBase):
    """Тесты рабочего времени для фирмы работающей ежедневно"""

    def setUp(self):
        self.city = City.objects.get(alias='irkutsk')

        firm = G(Firm, visible=True)
        self.address = G(Address, twenty_four_hour=False, firm_id=firm, city_id=self.city)
        for i in xrange(0, 7):
            G(Worktime, address=self.address, weekday=i,
              start_time=datetime.time(hour=8), end_time=datetime.time(hour=18),
              dinner_start_time=datetime.time(hour=12), dinner_end_time=datetime.time(hour=13))

    def test_general(self):
        """Основные проверки"""

        self.assertEqual(self.address.has_worktime, True)
        self.assertEqual(self.address.has_dinner, True)
        self.assertEqual(
            self.address.dinner_everyday_at_same_time,
            {'dinner_start_time': datetime.time(hour=12), 'dinner_end_time': datetime.time(hour=13)}
        )
        self.assertEqual(self.address.open_everyday_at_same_time, True)

    @freeze_time('2014-07-21 07:00')    # Пн
    def test_before_workday(self):
        """До рабочего дня"""

        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, u'откроется через 1 час')
        self.assertEqual(self.address.worktime_order, -3600)

    @freeze_time('2014-07-21 08:00')    # Пн
    def test_beginning_workday(self):
        """Начало рабочего дня"""

        self.assertEqual(self.address.current_worktime, Worktime.objects.get(address=self.address, weekday=0))
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, None)
        self.assertEqual(self.address.worktime_order, 3600 * 4)

    @freeze_time('2014-07-21 11:30')    # Пн
    def test_middle_workday_before_dinner(self):
        """Середина рабочего дня до обеда"""

        self.assertEqual(self.address.current_worktime, Worktime.objects.get(address=self.address, weekday=0))
        self.assertEqual(self.address.closing_in_3_hours, u'закроется на обед через 30 минут')
        self.assertEqual(self.address.open_in, None)
        self.assertEqual(self.address.worktime_order, 1800)

    @freeze_time('2014-07-21 12:00')    # Пн
    def test_beginning_dinner(self):
        """Начало обеда"""
        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.open_everyday_at_same_time, True)
        self.assertEqual(self.address.open_in, u'откроется через 1 час')
        self.assertEqual(self.address.worktime_order, -3600)

    @freeze_time('2014-07-21 12:20')    # Пн
    def test_middle_dinner(self):
        """Середина обеда"""

        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.open_everyday_at_same_time, True)
        self.assertEqual(self.address.open_in, u'откроется через 40 минут')
        self.assertEqual(self.address.worktime_order, -2400)

    @freeze_time('2014-07-21 13:00')    # Пн
    def test_ending_dinner(self):
        """Конец обеда"""

        self.assertEqual(self.address.current_worktime, Worktime.objects.get(address=self.address, weekday=0))
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, None)
        self.assertEqual(self.address.worktime_order, 3600 * 5)

    @freeze_time('2014-07-21 16:30')    # Пн
    def test_middle_workday_after_dinner(self):
        """Середина рабочего дня после обеда"""

        self.assertEqual(self.address.current_worktime, Worktime.objects.get(address=self.address, weekday=0))
        self.assertEqual(self.address.closing_in_3_hours, u'открыт еще 1 час 30 минут')
        self.assertEqual(self.address.open_in, None)
        self.assertEqual(self.address.worktime_order, 3600 + 1800)

    @freeze_time('2014-07-21 18:00')    # Пн
    def test_ending_workday(self):
        """Конец рабочего дня"""

        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, u'откроется через 14 часов')
        self.assertEqual(self.address.worktime_order, -3600 * 14)

    @freeze_time('2014-07-21 23:00')    # Пн
    def test_after_workday(self):
        """После рабочего дня"""

        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, u'откроется через 9 часов')
        self.assertEqual(self.address.worktime_order, -3600 * 9)


class EveryHourAddressWorktimeTest(UnitTestBase):
    """Тесты рабочего времени для фирмы работающей круглосуточно"""

    def setUp(self):
        self.city = City.objects.get(alias='irkutsk')

        firm = G(Firm, visible=True)
        self.address = G(Address, twenty_four_hour=True, firm_id=firm, city_id=self.city)
        for i in xrange(0, 7):
            G(Worktime, address=self.address, weekday=i,
              start_time=datetime.time(hour=8), end_time=datetime.time(hour=18),
              dinner_start_time=datetime.time(hour=12), dinner_end_time=datetime.time(hour=13))

    def test_general(self):
        """Основные проверки"""

        self.assertEqual(self.address.worktime_order, 3600 * 24 * 7)
        self.assertEqual(self.address.has_worktime, True)
        self.assertEqual(self.address.has_dinner, False)
        self.assertEqual(self.address.dinner_everyday_at_same_time, False)
        self.assertEqual(self.address.open_everyday_at_same_time, True)

    @freeze_time('2014-07-21 00:00')    # Пн
    def test_midnight(self):

        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, None)
        self.assertEqual(self.address.worktime_order, 3600 * 24 * 7)

    @freeze_time('2014-07-25 12:00')    # Пт
    def test_twelve_o_clock(self):

        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, None)
        self.assertEqual(self.address.worktime_order, 3600 * 24 * 7)

    @freeze_time('2014-07-27 23:59')    # Вс
    def test_one_minute_to_midnight(self):

        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, None)
        self.assertEqual(self.address.worktime_order, 3600 * 24 * 7)


class CustomAddressWorktimeTest(UnitTestBase):
    """Тесты рабочего времени для фирмы работающей как попало"""

    def setUp(self):
        self.city = City.objects.get(alias='irkutsk')

        firm = G(Firm, visible=True)
        self.address = G(Address, twenty_four_hour=False, firm_id=firm, city_id=self.city)
        G(Worktime, address=self.address, weekday=1,
          start_time=datetime.time(hour=10), end_time=datetime.time(hour=2))
        G(Worktime, address=self.address, weekday=2,
          start_time=datetime.time(hour=10), end_time=datetime.time(hour=2),
          dinner_start_time=datetime.time(hour=13), dinner_end_time=datetime.time(hour=14))
        G(Worktime, address=self.address, weekday=4,
          start_time=datetime.time(hour=1), end_time=datetime.time(hour=10),
          dinner_start_time=datetime.time(hour=12), dinner_end_time=datetime.time(hour=13))
        G(Worktime, address=self.address, weekday=6,
          start_time=datetime.time(hour=8), end_time=datetime.time(hour=3))

    def test_general(self):
        """Основные проверки"""

        self.assertEqual(self.address.has_worktime, True)
        self.assertEqual(self.address.has_dinner, True)
        self.assertEqual(self.address.dinner_everyday_at_same_time, False)
        self.assertEqual(self.address.open_everyday_at_same_time, False)

    @freeze_time('2014-07-21 01:00')    # Пн
    def test_open(self):
        """Утро понедельника, фирма еще открыта"""

        self.assertEqual(self.address.current_worktime, Worktime.objects.get(address=self.address, weekday=6))
        self.assertEqual(self.address.closing_in_3_hours, u'открыт еще 2 часа')
        self.assertEqual(self.address.open_in, None)

    @freeze_time('2014-07-21 04:00')    # Пн
    def test_close(self):
        """Утро понедельника, фирма уже закрыта"""

        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, u'откроется через 1 день')
        self.assertEqual(self.address.worktime_order, -(3600 * 24) - 3600 * 6)


class WorkdaysAddressWorktimeTest(UnitTestBase):
    """Тесты рабочего времени для фирмы работающей в рабочие дни"""

    def setUp(self):
        self.city = City.objects.get(alias='irkutsk')

        firm = G(Firm, visible=True)
        self.address = G(Address, twenty_four_hour=False, firm_id=firm, city_id=self.city)
        for i in xrange(0, 5):
            G(Worktime, address=self.address, weekday=i,
              start_time=datetime.time(hour=8), end_time=datetime.time(hour=18),
              dinner_start_time=datetime.time(hour=12), dinner_end_time=datetime.time(hour=13))

    def test_general(self):
        """Основные проверки"""

        self.assertEqual(self.address.has_worktime, True)
        self.assertEqual(self.address.has_dinner, True)
        self.assertEqual(
            self.address.dinner_everyday_at_same_time,
            {'dinner_start_time': datetime.time(hour=12), 'dinner_end_time': datetime.time(hour=13)}
        )
        self.assertEqual(self.address.open_everyday_at_same_time, False)

    @freeze_time('2014-07-25 18:30')    # Пт
    def test_weekend(self):
        """Фирма ушла на выходные"""

        self.assertEqual(self.address.current_worktime, None)
        self.assertEqual(self.address.closing_in_3_hours, None)
        self.assertEqual(self.address.open_in, u'откроется через 2 дня')
        # Разница в секундах между Пт 18:30 и Пн 8:00
        self.assertEqual(self.address.worktime_order, -3600 * 24 * 2 - 3600 * 13 - 1800)
