# -*- coding: utf-8 -*-

import datetime

from django_dynamic_fixture import G

from irk.map.models import Cities
from irk.tests.unit_base import UnitTestBase

from irk.weather.forecasts import Wind, Sky, ForecastDay, ForecastCurrent, ForecastByDays, ForecastDetailed, \
    ForecastMapCities, ForecastForCities
from irk.weather.models import WeatherCities, WeatherFact, WeatherTempHour, WeatherDetailed


class ForecastDayTest(UnitTestBase):
    """Тесты для прогноза погоды на день"""

    def setUp(self):
        self._stamp = datetime.datetime.now()
        self._city = Cities.objects.get(alias='irkutsk')
        # днем +15, ночью +5, ветер юго-восточный 5 м/с, облачно, небольшой снег, восход 6:15, заход 19:00,
        # источник foreca
        self._weather_city = G(
            WeatherCities, city=self._city, date=self._stamp.date(), day=15, night=5, wind=5, wind_t=3, nebulosity=3,
            precipitation=5, sun_v=datetime.time(6, 15), sun_z=datetime.time(19), stamp=self._stamp, source=7
        )

    def test_bool(self):
        """Определение истинности объекта"""

        # метка времени для который нет данных
        stamp = datetime.datetime(2015, 1, 1, 10, 15)
        self.assertFalse(ForecastDay(self._city, stamp))

        self.assertTrue(ForecastDay(self._city, self._stamp))

    def test_properties(self):
        """Проверка всех свойств"""

        forecast = ForecastDay(self._city, self._stamp)

        self.assertEqual(self._city, forecast.city)
        self.assertEqual(self._stamp, forecast.stamp)
        self.assertEqual(15, forecast.temp_day)
        self.assertEqual(5, forecast.temp_night)
        self.assertEqual('cloudy', forecast.sky.nebulosity_code)
        self.assertEqual('snow', forecast.sky.precipitation_code)
        self.assertEqual(5, forecast.wind.speed)
        self.assertEqual(u'юго-восточный', forecast.wind.long)
        self.assertEqual(datetime.time(6, 15), forecast.sunrise)
        self.assertEqual(datetime.time(19), forecast.sunset)


class ForecastCurrentTest(UnitTestBase):
    """Тесты для текущего прогноза погоды"""

    def setUp(self):
        self._stamp = datetime.datetime.now()
        self._city = Cities.objects.get(alias='irkutsk')
        # днем +15, ночью +5, ветер юго-восточный 5 м/с, облачно, небольшой снег, восход 6:15, заход 19:00,
        # источник foreca
        self._weather_city = G(
            WeatherCities, city=self._city, date=self._stamp.date(), day=15, night=5, wind=5, wind_t=3, nebulosity=3,
            precipitation=5, sun_v=datetime.time(6, 15), sun_z=datetime.time(19), stamp=self._stamp, source=7
        )

        # температура +10, по ощущениям +11, переменная облачность, небольшие осадки, ветер северо-западный 7 м/с,
        # давление 720 мм. рт. ст., влажность 80%, видимость 100 м.
        self._weather_fact = G(
            WeatherFact, city=self._city.id, datetime=self._stamp, temp=10, temp_feel=11, weather_code=3, nebulosity=2,
            mm=720, wind=7, wind_t=7, humidity=80, visibility=100,
        )

    def test_bool(self):
        """Определение истинности объекта"""

        # метка времени для который нет данных
        stamp = datetime.datetime(2015, 1, 1, 10, 15)
        self.assertFalse(ForecastCurrent(self._city, stamp))

        self.assertTrue(ForecastCurrent(self._city, self._stamp))

    def test_properties(self):
        """Проверка всех свойств"""

        forecast = ForecastCurrent(self._city, self._stamp)

        self.assertEqual(self._city, forecast.city)
        self.assertEqual(self._stamp, forecast.stamp)
        self.assertEqual(10, forecast.temp)
        self.assertEqual('variable', forecast.sky.nebulosity_code)
        self.assertEqual('sleet', forecast.sky.precipitation_code)
        self.assertEqual(7, forecast.wind.speed)
        self.assertEqual(u'северо-западный', forecast.wind.long)
        self.assertEqual(720, forecast.pressure)
        self.assertEqual(80, forecast.humidity)
        self.assertEqual(u'100 м.', forecast.visibility)

    def test_has_charts(self):
        """Проверка на наличие графиков"""

        forecast = ForecastCurrent(self._city, self._stamp)
        self.assertFalse(forecast.has_charts())

        # Результат has_charts() сохраняется в кэш, поэтому очищаем его, чтобы тест сработал корректно
        self.cache_clear()

        for i in range(50):
            G(
                WeatherTempHour, temp=10+i, mm=760-i, city=self._city.id,
                time=self._stamp-datetime.timedelta(minutes=i)
            )

        self.assertTrue(forecast.has_charts())


class ForecastByDaysTest(UnitTestBase):
    """Тесты прогнозов на несколько дней"""

    def setUp(self):
        self._stamp = datetime.datetime.now()
        self._city = Cities.objects.get(alias='irkutsk')

        for i in range(15):
            date = self._stamp + datetime.timedelta(days=i)
            G(WeatherCities, city=self._city, date=date, source=7)

    def test_get_forecasts(self):
        """Проверка прогнозов"""

        forecasts = ForecastByDays(self._city, self._stamp.date(), count=12).get_forecasts()

        self.assertEqual(12, len(forecasts))
        # Имеются все необходимые ключи
        for forecast in forecasts:
            self.assertListContains(['date', 'temp', 'sky', 'wind'], forecast.keys())


class ForecastDetailedTest(UnitTestBase):
    """Тесты подробного прогноза на 3 дня"""

    def setUp(self):
        self._stamp = datetime.datetime.now()
        self._city = Cities.objects.get(alias='irkutsk')

        for i in range(3):
            date = self._stamp + datetime.timedelta(days=i)
            for hour in [6, 12, 18, 21]:
                stamp = date.replace(hour=hour)
                G(WeatherDetailed, city=self._city, datetime=stamp, day=stamp.day, hour=hour)

    def test_get_forecasts(self):
        """Проверка прогнозов"""

        stamp = self._stamp.replace(hour=7)
        # [(date, forecasts), (date, forecasts), ...]
        forecasts_by_day = list(ForecastDetailed(self._city, stamp).get_forecasts())

        # прогнозы на 3 дня
        self.assertEqual(3, len(forecasts_by_day))
        # Имеются все необходимые ключи
        for date, forecasts in forecasts_by_day:
            for forecast in forecasts:
                self.assertListContains(
                    ['datetime', 'temp', 'period', 'sky', 'wind', 'humidity', 'pressure'], forecast.keys()
                )

    def test_forecasts_for_current_day(self):
        """Прогнозы для текущего дня в зависимости от времени запроса"""

        stamp = self._stamp.replace(hour=5)
        forecasts_by_day = list(ForecastDetailed(self._city, stamp).get_forecasts())
        self.assertEqual(4, len(forecasts_by_day[0][1]))

        stamp = self._stamp.replace(hour=7)
        forecasts_by_day = list(ForecastDetailed(self._city, stamp).get_forecasts())
        self.assertEqual(4, len(forecasts_by_day[0][1]))

        stamp = self._stamp.replace(hour=13)
        forecasts_by_day = list(ForecastDetailed(self._city, stamp).get_forecasts())
        self.assertEqual(3, len(forecasts_by_day[0][1]))

        stamp = self._stamp.replace(hour=19)
        forecasts_by_day = list(ForecastDetailed(self._city, stamp).get_forecasts())
        self.assertEqual(2, len(forecasts_by_day[0][1]))

        stamp = self._stamp.replace(hour=22)
        forecasts_by_day = list(ForecastDetailed(self._city, stamp).get_forecasts())
        self.assertEqual(1, len(forecasts_by_day[0][1]))

    def test_get_hour(self):
        """Проверка приведения часов"""

        tests = {
            # hour: result
            1: 6,
            5: 6,
            6: 6,
            7: 6,
            11: 6,
            12: 12,
            13: 12,
            17: 12,
            18: 18,
            19: 18,
            20: 18,
            21: 21,
            22: 21,
        }

        forecasts_detailed = ForecastDetailed(self._city, self._stamp)

        for hour, result in tests.items():
            stamp = self._stamp.replace(hour=hour)
            self.assertEqual(result, forecasts_detailed._get_hour(stamp))


class ForecastMapCitiesTest(UnitTestBase):
    """Тесты прогнозов погоды на карте"""

    def setUp(self):
        self._stamp = datetime.datetime.now()
        self._cities = {
            'irkutsk': Cities.objects.get(alias='irkutsk'),
            'angarsk': Cities.objects.get(alias='angarsk'),
        }

        for i in range(5):
            stamp = self._stamp - datetime.timedelta(hours=i)
            for city_alias in self._cities:
                G(WeatherFact, city=self._cities[city_alias].id, datetime=stamp, day=u'{:%m%d}'.format(stamp.date()))

    def test_forecasts(self):
        """Проверка прогнозов"""

        forecasts = list(ForecastMapCities(self._stamp).get_forecasts())

        self.assertEqual(2, len(forecasts))
        for forecast in forecasts:
            self.assertListContains(['city', 'coords', 'temp', 'icon_class', 'datetime'], forecast.keys())

    def test_is_night(self):
        """Проверка на ночь для города"""

        city = self._cities.get('irkutsk')

        # время до рассвета
        stamp = datetime.datetime(2015, 10, 27, 6)
        G(WeatherCities, city=city, date=stamp.date(), sun_v=datetime.time(7, 10), sun_z=datetime.time(18, 30))
        forecast = ForecastMapCities(stamp)
        self.assertTrue(forecast._is_night(city.id))

        # время после рассвета
        stamp = datetime.datetime(2015, 10, 28, 9)
        G(WeatherCities, city=city, date=stamp.date(), sun_v=datetime.time(7, 10), sun_z=datetime.time(18, 30))
        forecast = ForecastMapCities(stamp)
        self.assertFalse(forecast._is_night(city.id))


class ForecastForCitiesTest(UnitTestBase):
    """Тесты для прогнозов для списка городов"""

    def setUp(self):
        self._stamp = datetime.datetime.now()
        self._cities = {
            'irkutsk': Cities.objects.get(alias='irkutsk'),
            'angarsk': Cities.objects.get(alias='angarsk'),
        }

        for i in range(5):
            stamp = self._stamp - datetime.timedelta(hours=i)
            for city_alias in self._cities:
                G(WeatherFact, city=self._cities[city_alias].id, datetime=stamp, day=u'{:%m%d}'.format(stamp.date()))

    def test_add_forecasts(self):
        """Проверка добавления прогнозов к списку городов"""

        cities = self._cities.values()
        cities = ForecastForCities(self._stamp).add_forecasts(cities)

        for city in cities:
            self.assertTrue(hasattr(city, 'forecast'))
            self.assertListContains(['temp', 'sky'], city.forecast.keys())


class WindTest(UnitTestBase):
    """Тесты класса Wind"""

    def test_bool(self):
        """Определение истинности объекта"""

        self.assertTrue(Wind(1, 1))
        self.assertTrue(Wind(None, 1))
        self.assertTrue(Wind(1, None))
        self.assertFalse(Wind(None, None))

    def test_is_calm(self):
        """Определение штиля"""

        self.assertTrue(Wind(0, 1).is_calm())
        self.assertTrue(Wind(5, 0).is_calm())
        self.assertFalse(Wind(1, 1).is_calm())


class SkyTest(UnitTestBase):
    """Тесты класса Sky"""

    def test_bool(self):
        """Определение истинности объекта"""

        self.assertTrue(Sky(1, 1))
        self.assertTrue(Sky(None, 1))
        self.assertTrue(Sky(1, None))
        self.assertFalse(Sky(None, None))

    def test_icon_class(self):
        """CSS-класс иконки"""

        self.assertEqual('cloudy-rain', Sky(3, 4).icon_class)
        self.assertEqual('cloudy-rain night', Sky(3, 4, for_night=True).icon_class)

        self.assertEqual('fair-lack', Sky(50, 50).icon_class, msg=u'Неверные значения для облачности и осадков')
