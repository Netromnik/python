# -*- coding: utf-8 -*-

import datetime

from django_dynamic_fixture import G

from irk.map.models import Cities
from irk.tests.unit_base import UnitTestBase

from irk.weather.models import WishForDay, WishForConditions, MeteoCentre, WeatherCities
from irk.weather.controllers import WishController
from irk.weather.forecasts import ForecastDay


class WishControllerTest(UnitTestBase):
    """Тесты контроллера пожеланий"""

    fixtures = UnitTestBase.fixtures + ['months']
    conditions = [
        {'text': 'default'},
        {'text': 'test_storm', 'months': [1], 'is_storm': True},
        {'text': 'test_strong_wind', 'months': [1], 'is_strong_wind': True},
        {'text': 'test_only_temp', 'months': [1], 't_min': -10, 't_max': -5},
        {'text': 'test_only_cloudy', 'months': [1], 'is_cloudy': True},
        {'text': 'test_only_variable', 'months': [1], 'is_variable': True},
        {'text': 'test_only_precipitation', 'months': [1], 'is_precipitation': True},
        {'text': 'test_1', 'months': [1], 't_min': 0, 't_max': 5, 'is_precipitation': True, 'is_cloudy': True},
        {'text': 'test_2', 'months': [1], 't_min': 0, 't_max': 10, 'is_precipitation': True, 'is_variable': True},
        {'text': 'test_invalid_rule', 'months': [1], 't_min': 20, 't_max': 20, 'is_cloudy': True, 'is_variable': True},
        {'text': 'test_not_wish_for_month', 'months': [2], 't_min': 0, 't_max': 10},
        {'text': 'test_invalid_temp', 'months': [1], 't_min': -20, 't_max': -30},
        {'text': 'test_skip_storm', 'months': [1], 't_min': 30, 't_max': 30, 'is_storm': True, 'is_variable': True},
        {'text': 'test_skip_strong_wind', 'months': [1], 't_min': 40, 't_max': 40, 'is_strong_wind': True},
        {'text': 'test_rotation_1', 'months': [3], 't_min': 0, 't_max': 10, 'is_variable': True},
        {'text': 'test_rotation_2', 'months': [3], 't_min': 0, 't_max': 10, 'is_variable': True},
        {'text': 'test_rotation_3', 'months': [3], 't_min': 0, 't_max': 10, 'is_variable': True},
    ]

    def setUp(self):
        self._stamp = datetime.datetime(2015, 1, 1, 10, 0)
        self._city = Cities.objects.get(alias='irkutsk')

        for condition in self.conditions:
            G(WishForConditions, fill_nullable_fields=False, **condition)

    def test_wish_for_day(self):
        """Пожелание на день"""

        wish = G(WishForDay, date=self._stamp.date())
        forecast = ForecastDay(self._city, self._stamp)

        self.assertEqual(wish, WishController(forecast, None).get_wish())

    def test_storm(self):
        """Пожелание когда шторм"""

        forecast = ForecastDay(self._city, self._stamp)
        meteocentre = G(MeteoCentre, stamp=self._stamp.date(), storm_caption='Storm', storm_content='Run')

        wish = WishController(forecast, meteocentre).get_wish()
        self.assertEqual('test_storm', wish.text)

    def test_strong_wind(self):
        """Пожелание когда сильный ветер (> 20 м/с)"""

        self._create_weather_cities(wind=25)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('test_strong_wind', wish.text)

    def test_not_wish_for_month(self):
        """Нет условия для определенного месяца"""

        # 10 мая 2015 года.
        stamp = datetime.datetime(2015, 5, 10, 10, 0)
        self._create_weather_cities(stamp=stamp, day=10)
        forecast = ForecastDay(self._city, stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('default', wish.text)

    def test_not_wish_for_temp(self):
        """Нет условия для температуры"""

        self._create_weather_cities(day=15)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('default', wish.text)

    def test_only_temp(self):
        """Только температура"""

        self._create_weather_cities(day=-5)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('test_only_temp', wish.text)

    def test_only_cloudy(self):
        """Только облачность/пасмурно"""

        self._create_weather_cities(nebulosity=4)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('test_only_cloudy', wish.text)

    def test_only_variable(self):
        """Только переменная облачность"""

        self._create_weather_cities(nebulosity=2)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('test_only_variable', wish.text)

    def test_only_precipitation(self):
        """Только осадки"""

        self._create_weather_cities(precipitation=4)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('test_only_precipitation', wish.text)

    def test_1(self):
        """Температура, осадки и облачность"""

        self._create_weather_cities(day=5, nebulosity=4, precipitation=4)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('test_1', wish.text)

    def test_2(self):
        """Температура, осадки и переменная облачность"""

        self._create_weather_cities(day=5, nebulosity=2, precipitation=4)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('test_2', wish.text)

    def test_invalid_rule(self):
        """Не может быть облачно и переменная облачность одновременно"""

        self._create_weather_cities(day=20, nebulosity=3)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('default', wish.text)

    def test_invalid_temp(self):
        """Неверно указана температура"""

        self._create_weather_cities(day=-25)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('default', wish.text)

    def test_skip_storm(self):
        """Пожелание когда пропущен шторм"""

        self._create_weather_cities(day=30, nebulosity=2)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('default', wish.text)

    def test_skip_strong_wind(self):
        """Пожелание когда пропущен сильный ветер (> 15 м/с)"""

        self._create_weather_cities(day=40, wind=14)
        forecast = ForecastDay(self._city, self._stamp)

        wish = WishController(forecast, None).get_wish()
        self.assertEqual('default', wish.text)

    def test_rotation(self):
        """Проверка ротации пожеланий на одинаковые условия в течении нескольких дней"""

        forecasts = []
        # Одинаковый прогноз на 3 дня
        for i in xrange(1, 4):
            stamp = datetime.datetime(2015, 3, i, 10, 0)
            self._create_weather_cities(day=5, nebulosity=2, stamp=stamp)
            forecasts.append(ForecastDay(self._city, stamp))

        texts = set()

        wish = WishController(forecasts[0], None).get_wish()
        texts.add(wish.text)

        wish = WishController(forecasts[1], None).get_wish()
        texts.add(wish.text)

        wish = WishController(forecasts[2], None).get_wish()
        texts.add(wish.text)

        wish = WishController(forecasts[0], None).get_wish()
        texts.add(wish.text)

        self.assertItemsEqual(
            {'test_rotation_1', 'test_rotation_2', 'test_rotation_3'},
            texts
        )

    def _create_weather_cities(self, **kwargs):
        """Создать объект WeatherCities"""

        stamp = kwargs.pop('stamp', None) or self._stamp

        return G(WeatherCities, city=self._city, date=stamp.date(), fill_nullable_fields=False, **kwargs)
