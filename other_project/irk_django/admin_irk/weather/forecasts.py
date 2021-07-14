# -*- coding: utf-8 -*-

"""
Модуль содержащий классы для представления различных прогнозов погоды.
"""


import datetime
from collections import OrderedDict

from django.core.cache import cache
from django.db.models import QuerySet

from irk.map.models import Cities

from irk.weather import settings as app_settings
from irk.weather.models import WeatherFact, WeatherCities, WeatherDetailed, WeatherTempHour

EMPTY_VALUE = object()


class ForecastDay(object):
    """Прогноз погоды для города на день"""

    def __init__(self, city, stamp):
        """
        :param map.Cities city: город
        :param datetime.datetime stamp: временная метка
        """

        self._city = city
        self._stamp = stamp
        self._weather_cities = WeatherCities.objects.filter(city=self._city, date=self._stamp.date()).first()

        # Если данных для прогноза нет, подставляем пустые объекты. Таким образом методы будут возращать None,
        # а не поднимать исключение
        if not self._weather_cities:
            self._weather_cities = WeatherCities()

    @property
    def city(self):
        """Город"""

        return self._city

    @property
    def stamp(self):
        """Дата и время прогноза"""

        return self._stamp

    @property
    def temp_day(self):
        """Температура днем"""

        return self._weather_cities.day

    @property
    def temp_night(self):
        """Температура ночью"""

        return self._weather_cities.night

    @property
    def sky(self):
        """Облачность и осадки"""

        return Sky(self._weather_cities.nebulosity, self._weather_cities.precipitation)

    @property
    def wind(self):
        """Направление и скорость ветра"""

        return Wind(self._weather_cities.wind, self._weather_cities.wind_t)

    @property
    def sunrise(self):
        """Восход солнца"""

        return self._weather_cities.sun_v

    @property
    def sunset(self):
        """Заход солнца"""

        return self._weather_cities.sun_z

    def __nonzero__(self):
        """
        Если нет данных из модели WeatherCities, то возращается False
        """

        return bool(self._weather_cities.id)


class ForecastCurrent(ForecastDay):
    """
    Текущий прогноз погоды для города.

    Класс строится на основе ForecastDay, и переопределяет свойсва связанные с текущим прогнозом погоды.
    """

    def __init__(self, *args, **kwargs):
        super(ForecastCurrent, self).__init__(*args, **kwargs)

        start_date = self._stamp.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = self._stamp.replace(hour=23, minute=59, second=59, microsecond=0)
        self._weather_fact = WeatherFact.objects \
            .filter(city=self._city.id, datetime__range=(start_date, end_date)) \
            .order_by('-datetime') \
            .first()

        if not self._weather_fact:
            self._weather_fact = WeatherFact()

    @property
    def temp(self):
        """Температура"""

        return self._weather_fact.temp

    @property
    def sky(self):
        """Облачность и осадки"""

        try:
            # Считаем, что сейчас ночь, если текущее время не попадает в промежуток между восходом и заходом + 2 часа
            sunset = self.sunset.replace(hour=self.sunset.hour + 2)
            is_night = not (self.sunrise < self.stamp.time() < sunset)
        except (TypeError, AttributeError, ValueError):
            is_night = False

        return Sky(self._weather_fact.nebulosity, self._weather_fact.weather_code, for_night=is_night)

    @property
    def wind(self):
        """Направление и скорость ветра"""

        return Wind(self._weather_fact.wind, self._weather_fact.wind_t)

    @property
    def humidity(self):
        """Влажность"""

        return self._weather_fact.humidity

    @property
    def pressure(self):
        """Давление"""

        return self._weather_fact.mm

    @property
    def visibility(self):
        """Видимость"""

        value = self._weather_fact.visibility

        if value > 1000:
            return (u'%.1f км.' % (value / 1000.)).replace('.', ',', 1)
        return u'%d м.' % value

    def has_charts(self):
        """Проверяет возможно ли отображение графика для текущей погоды"""

        cache_key = 'weather:has_charts:%s' % self.city.id
        value = cache.get(cache_key, default=EMPTY_VALUE)
        if value == EMPTY_VALUE:
            start_date = self.stamp - datetime.timedelta(days=1)
            value = WeatherTempHour.objects.filter(city=self.city.id, time__gte=start_date).count() >= 45

            cache.set(cache_key, value, 60)

        return bool(value)

    def __nonzero__(self):
        """
        Если нет данных из модели WeatherFact или WeatherCities, то возращается False
        """

        return all([self._weather_fact.id, self._weather_cities.id])


class ForecastByDays(object):
    """Краткий прогноз погоды для города на несколько дней"""

    def __init__(self, city, start_date, count=None):
        """
        :param Cities city: город
        :param datetime.date start_date: первый день для прогноза
        :param int count: количество дней (включая start_date)
        """
        self._city = city
        self._start_date = start_date
        self._count = count or app_settings.WEATHER_FORECAST_DAYS

    @property
    def city(self):
        """Город"""

        return self._city

    def get_forecasts(self):
        """Загрузить данные для прогноза"""

        end_date = self._start_date + datetime.timedelta(days=self._count - 1)
        weather_cities = WeatherCities.objects \
            .filter(city=self._city, date__range=[self._start_date, end_date]) \
            .order_by('date')
        
        forecasts = []
        for wc in weather_cities:
            forecasts.append(self._prepare(wc))
        
        return forecasts

    def _prepare(self, weather_city):
        """
        Подготовить данные о прогнозе.
        
        :type weather_city: WeatherCities
        """

        return {
            'date': weather_city.date,
            'sky': Sky(weather_city.nebulosity, weather_city.precipitation),
            'temp': {'day': weather_city.day, 'night': weather_city.night},
            'wind': Wind(weather_city.wind, weather_city.wind_t),
        }


class ForecastDetailed(object):
    """Подробный прогноз погоды для города на несколько дней"""

    def __init__(self, city, stamp, count=None):
        self._city = city
        self._stamp = stamp
        self._count = count or app_settings.WEATHER_FORECAST_DETAILED_DAYS

    @property
    def city(self):
        """Город"""

        return self._city
        
    def get_forecasts(self):
        """Получить прогнозы"""

        hour = self._get_hour(self._stamp)
        start_date = self._stamp.replace(hour=hour, minute=0, second=0, microsecond=0)
        end_date = start_date + datetime.timedelta(days=self._count - 1)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=0)

        weather_details = WeatherDetailed.objects \
            .filter(city=self._city, datetime__range=[start_date, end_date]) \
            .order_by('datetime', 'hour')
        
        forecasts = OrderedDict()
        for wd in weather_details:
            forecasts.setdefault(wd.datetime.date(), []).append(self._prepare(wd))

        return forecasts.iteritems()

    def _prepare(self, weather_detailed):
        """Подготовить данные о прогнозе."""

        is_night = weather_detailed.hour == 21

        return {
            'datetime': weather_detailed.datetime,
            'temp': {'from': weather_detailed.temp_from, 'to': weather_detailed.temp_to},
            'period': {6: u'утром', 12: u'днем', 18: u'вечером', 21: u'ночью'}.get(weather_detailed.hour, u''),
            'sky': Sky(weather_detailed.nebulosity, weather_detailed.precipitation, is_night),
            'wind': Wind(weather_detailed.wind, weather_detailed.wind_t),
            'humidity': weather_detailed.humidity,
            'pressure': weather_detailed.mm,
        }

    def _get_hour(self, stamp):
        """Получить приведенный час для метки времени"""

        periods = {
            # утро
            (0, 12): 6,
            # день
            (12, 18): 12,
            # вечер
            (18, 21): 18,
            # ночь
            (21, 23): 21,

        }

        hour = stamp.hour
        for limits in periods.keys():
            if limits[0] <= hour < limits[1]:
                return periods[limits]

        return hour


class ForecastMapCities(object):
    """
    Текущая погода по городам области.

    Используется для карты погоды.
    """

    def __init__(self, stamp):
        self._stamp = stamp

    def get_forecasts(self):
        """Загрузить данные для прогноза"""

        filters = {
            'datetime__year': self._stamp.year,
            'day': u'{:%m%d}'.format(self._stamp.date())
        }

        weather_facts = WeatherFact.objects \
            .filter(**filters) \
            .values('city', 'temp', 'weather_code', 'nebulosity', 'datetime') \
            .order_by('city', '-datetime')

        # Для каждого города оставляем данные за последний момент времени
        forecasts = []
        processed_cities = set()
        for wf in weather_facts:
            if not wf['city'] in processed_cities:
                forecasts.append(wf)
                processed_cities.add(wf['city'])

        for forecast in forecasts:
            city_id = forecast['city']
            city = Cities.objects.filter(id=city_id).values('name', 'center', 'weather_label').first()
            if not city:
                continue
            point = city['weather_label'] or city['center']
            # Пропускаем города у которых нет координат
            if not point:
                continue

            yield {
                'city': {'id': city_id, 'name': city['name']},
                'coords': point.coords,
                'temp': forecast['temp'],
                'icon_class': Sky(forecast['nebulosity'], forecast['weather_code'], self._is_night(city_id)).icon_class,
                'datetime': forecast['datetime'],
            }

    def _is_night(self, city_id):
        """Наступила ночь?"""

        limits = WeatherCities.objects.filter(city=city_id, date=self._stamp.date()).values('sun_v', 'sun_z').first()
        if not limits:
            return False

        try:
            # Считаем, что сейчас ночь, если текущее время не попадает в промежуток между восходом и заходом + 2 часа
            sunset = limits['sun_z'].replace(hour=limits['sun_z'].hour + 2)
            is_night = not (limits['sun_v'] < self._stamp.time() < sunset)
        except (TypeError, ValueError):
            is_night = False

        return is_night


class ForecastForCities(object):
    """Текущий прогноз погоды для городов"""

    def __init__(self, stamp):
        self._stamp = stamp

    def add_forecasts(self, cities):
        """Добавить прогнозы к объектам городов"""

        cities_ids = self._get_cities_ids(cities)
        forecasts = self._get_forecasts(cities_ids)

        for city in cities:
            city.forecast = forecasts.get(city.id)

        return cities

    def _get_cities_ids(self, cities):
        """
        Получить идентификаторы городов

        :param cities: список городов
        :type cities: QuerySet or list or tuple
        :rtype: list or tuple
        """

        if isinstance(cities, QuerySet):
            return list(cities.values_list('id', flat=True))

        if isinstance(cities, (list, tuple)):
            return [city.id for city in cities]

        return []

    def _get_forecasts(self, cities_ids):
        """Получить прогнозы погоды для городов по идентификаторам"""

        filters = {
            'city__in': cities_ids,
            'datetime__year': self._stamp.year,
            'day': u'{:%m%d}'.format(self._stamp.date())
        }

        data = WeatherFact.objects \
            .filter(**filters) \
            .values('city', 'temp', 'weather_code', 'nebulosity', 'datetime') \
            .order_by('city', '-datetime')

        # Для каждого города оставляем данные за последний момент времени
        forecasts = {}
        for row in data:
            if not row['city'] in forecasts:
                forecasts[row['city']] = {
                    'temp': row['temp'],
                    'sky': Sky(row['nebulosity'], row['weather_code'])
                }

        return forecasts


class Wind(object):
    """Ветер"""

    TITLES = {
        0: {'long': u'штиль', 'short': u'штиль'},
        1: {'long': u'северо-восточный', 'short': u'сев.-вост.'},
        2: {'long': u'восточный', 'short': u'восточный'},
        3: {'long': u'юго-восточный', 'short': u'юго-вост.'},
        4: {'long': u'южный', 'short': u'южный'},
        5: {'long': u'юго-западный', 'short': u'юго-зап.'},
        6: {'long': u'западный', 'short': u'западный'},
        7: {'long': u'северо-западный', 'short': u'сев.-зап.'},
        8: {'long': u'северный', 'short': u'северный'},
        99: {'long': u'переменный', 'short': u'переменный'},
    }

    def __init__(self, speed, direction):
        """
        :param int speed: скорость ветра
        :param int direction: направление ветра
        """
        self._speed = speed
        self._direction = direction

    @property
    def speed(self):
        """Скорость ветра"""

        return self._speed

    @property
    def long(self):
        """Длинное описание"""

        return self.TITLES.get(self._direction, {}).get('long', u'')

    @property
    def short(self):
        """Короткое описание"""

        return self.TITLES.get(self._direction, {}).get('short', u'')

    def is_calm(self):
        """Штиль"""

        return self.speed == 0 or self._direction == 0

    def __unicode__(self):
        chunks = []
        if self.long:
            chunks.append(self.long)
        if self.speed:
            chunks.append(u'{} м/с'.format(self.speed))

        return u', '.join(chunks)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __repr__(self):
        return u'<Wind: {}>'.format(self.__unicode__()).encode('utf-8')

    def __nonzero__(self):
        return self._speed is not None or self._direction is not None


class Sky(object):
    """
    Облачность и осадки.

    Все осадки сводятся к 5 состояниям: нет осадков, дождь, снег, дождь со снегом, гроза.
    """

    PRECIPITATION_TITLES = {
        1: u'без осадков',
        2: u'преимущественно без осадков',
        3: u'небольшие осадки',
        4: u'небольшой дождь',
        5: u'небольшой снег',
        6: u'осадки',
        7: u'дождь',
        8: u'снег',
        9: u'метель',
        10: u'дождь, гроза',
        11: u'дождь, град',
    }

    PRECIPITATION_CODES = {
        'lack': [1, 2],
        'rain': [4, 7, 11],
        'snow': [5, 8, 9],
        'sleet': [3, 6],
        'storm': [10],
    }

    NEBULOSITY_TITLES = {
        1: u'ясно',
        2: u'переменная облачность',
        3: u'облачно',
        4: u'пасмурно',
    }

    NEBULOSITY_CODES = {
        'fair': [1],
        'variable': [2],
        'cloudy': [3, 4],
    }

    def __init__(self, nebulosity, precipitation, for_night=False):
        """
        :param int nebulosity: облачность
        :param int precipitation: осадки
        :param bool for_night: Если True, используеются версии иконок для ночного времени суток.
        """
        self._nebulosity = nebulosity
        self._precipitation = precipitation
        self.for_night = for_night

    @property
    def icon_class(self):
        """
        CSS класс для иконки облачности и осадков.
        """

        css_class = u'{}-{}'.format(self.nebulosity_code, self.precipitation_code)

        # Модификатор для ночных иконок
        if self.for_night:
            css_class += u' night'

        return css_class

    @property
    def nebulosity(self):
        """Текстовое описание облачности"""

        return self.NEBULOSITY_TITLES.get(self._nebulosity, u'')

    @property
    def precipitation(self):
        """Текстовое описание осадков"""

        return self.PRECIPITATION_TITLES.get(self._precipitation, u'')

    @property
    def nebulosity_code(self):
        """Получить код для облачности"""

        for key, values in self.NEBULOSITY_CODES.items():
            if self._nebulosity in values:
                return key

        return 'fair'

    @property
    def precipitation_code(self):
        """Получить код для осадков"""

        for key, values in self.PRECIPITATION_CODES.items():
            if self._precipitation in values:
                return key

        return 'lack'

    def __unicode__(self):
        chunks = []
        if self.nebulosity:
            chunks.append(self.nebulosity)

        if self.precipitation:
            chunks.append(self.precipitation)

        return u', '.join(chunks)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __repr__(self):
        return u'<Sky: {}>'.format(self.__unicode__()).encode('utf-8')

    def __nonzero__(self):
        return self._nebulosity is not None or self._precipitation is not None
