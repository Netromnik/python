# -*- coding: utf-8 -*-

"""Граббер погоды openweathermap.com"""

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import logging

import ephem
from django.core.management.base import BaseCommand

from irk.utils.grabber import proxy_requests
from irk.utils.helpers import int_or_none
from irk.weather import settings as app_settings
from irk.weather.models import WeatherFact, WeatherTempHour, WeatherDetailed, WeatherCities

logger = logging.getLogger(__name__)

# Подробный прогноз на 5 дней вперед
WEATHER_3HOUR_URL = 'https://api.openweathermap.org/data/2.5/forecast?lang=ru&units=metric'
# Фактическая погода
WEATHER_CURRENT_URL = 'https://api.openweathermap.org/data/2.5/weather?lang=ru&units=metric'

# Соответствие между id города в базе и id OWP
WEATHER_CITY_ID_MAP = {
    1: 2023469,  # Иркутск
    2: 2027667,  # Ангарск
    3: 2051523,  # Братск
    4: 2014022,  # Усолье-Сибирское
    5: 2013952,  # Усть-Илимск
    6: 2026979,  # Байкальск
    7: 2014927,  # Тулун
    8: 2025527,  # Черемхово
    9: 2016764,  # Шелехов
    10: 2020744,  # Листвянка
    11: 1497549,  # Нижнеудинск
    12: 2055166,  # Саянск
    13: 2016422,  # Слюдянка
    14: 2026583,  # Бодайбо
    15: 1489870,  # Тайшет
    16: 2022143,  # Хужир
    17: {'lat': 51.90, 'lon': 102.43},  # Аршан
    20: 2014407,  # Улан-Удэ
    32: 2016910,  # Северобайкальск
    33: 2013986,  # Усть-Баргузин
    34: 2013894,  # Усть-Ордынский
    36: 2021066,  # Кяхта
    37: 2023876,  # Гремячинск
    38: 2023778,  # Гусиноозерск
    39: 2012702,  # Залари
    40: {'lat': 52.48, 'lon': 106.96},  # Энхалук
    41: {'lat': 51.68, 'lon': 101.68},  # Нилова Пустынь
}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--detailed',
                            action='store_true',
                            dest='detailed',
                            default=False)

        parser.add_argument('--current',
                            action='store_true',
                            dest='current',
                            default=False)

    def handle(self, *args, **options):
        logger.debug('Weather foreca grabber started at %s' % datetime.datetime.now().isoformat())

        if options['detailed']:
            self.detailed()
        if options['current']:
            self.current()

        logger.debug('Weather foreca grabber stopped at %s' % datetime.datetime.now().isoformat())

    def get_precipitation(self, code):
        """
        Парсинг значения осадков из кода картинки
        Описание кодов погоды: https://openweathermap.org/weather-conditions
        """
        code = str(code)

        def check_code(code):
            id_map = {
                1: ['8', '7'],  # 'без осадков'
                2: [],  # 'преимущественно без осадков'  # Не используется
                3: ['300', '310', '615', ],  # 'небольшие осадки'
                4: ['500', '520', ],  # 'небольшой дождь'
                5: ['600', '620', ],  # 'небольшой снег'
                6: ['3', '611', ],  # 'осадки'
                7: ['5', ],  # 'дождь'
                8: ['6', ],  # 'снег'
                9: [],  # 'метель'  # Не используется
                10: ['2', ],  # 'дождь, гроза'
                11: [],  # 'дождь, град'  # Нет данных на OWM
            }

            for irk_id, ow_codes in id_map.items():
                if code in ow_codes:
                    return irk_id

        try:
            group_code = code[1]
        except TypeError:
            group_code = '8'

        precipitation = check_code(code)
        if not precipitation:
            precipitation = check_code(group_code)

        return precipitation

    def get_nebulosity(self, image_code):
        """Сопоставить облачность от OWP с облачностью от irk.ru"""

        try:
            image_code = image_code[:2]
        except TypeError:
            image_code = '01'

        id_map = {
            1: ['01', ],  # ясно
            2: ['02', ],  # переменная облачность
            3: ['03', ],  # облачно
            4: ['04', '09', '10', '11', '13', '50', ],  # пасмурно
        }

        nebulosity = 1
        for irk_id, ow_icons in id_map.items():
            if image_code in ow_icons:
                nebulosity = irk_id
                break

        return nebulosity

    def pressure_hpa_to_mm(self, pressure):
        pressure = int_or_none(pressure)
        if pressure:
            return int(pressure * 0.75)
        return None

    def wind_degree_convent(self, deg):
        """Конвертирование градусов в наши значения"""

        if not deg:
            return 0

        if 22.5 < deg <= 67.5:
            return 1
        if 67.5 < deg <= 112.5:
            return 2
        if 112.5 < deg <= 157.5:
            return 3
        if 157.5 < deg <= 202.5:
            return 4
        if 202.5 < deg <= 247.5:
            return 5
        if 247.5 < deg <= 292.5:
            return 6
        if 292.5 < deg <= 337.5:
            return 7
        if deg <= 22.5 or deg > 337.5:
            return 8

    def send_request(self, url, owp_id):
        """Запрос на OWP"""
        params = {'appid': app_settings.WEATHER_OPENWEATHERMAP_TOKEN}

        if isinstance(owp_id, dict):
            params['lon'] = owp_id['lon']
            params['lat'] = owp_id['lat']
        else:
            params['id'] = owp_id

        try:
            r = proxy_requests.get(url, params=params)
            r.raise_for_status()
        except proxy_requests.HTTPError as e:
            logger.warning('Openweathermap forecast data is not available. Error {}'.format(e))
            return

        return r.json()

    def current(self):
        """Граббер текущей погоды"""

        for city_id, owp_id in WEATHER_CITY_ID_MAP.items():

            data = self.send_request(WEATHER_CURRENT_URL, owp_id)

            if not data:
                continue

            date = datetime.datetime.fromtimestamp(data['dt'])

            try:
                weather = WeatherFact.objects.filter(city=city_id, datetime=date)[0]
            except IndexError:
                weather = WeatherFact(city=city_id, datetime=date, day='{:02d}{:02d}'.format(date.month, date.day))

            weather.temp = int_or_none(round(data['main']['temp']))
            weather.mm = self.pressure_hpa_to_mm(data['main']['pressure'])

            # OWM стало отдавать давление без учета высоты над уровнем моря с 11.01.2019 22:00
            if weather.mm:
                # 0.9464 - высчитано по формуле p*e^(-h/7.99) где h высота иркутска над уровнем моря
                weather.mm = int(weather.mm * 0.9464)

            weather.wind = int_or_none(round(data['wind']['speed']))
            weather.humidity = int_or_none(data['main']['humidity'])
            weather.visibility = int_or_none(data['visibility']) if 'visibility' in data else 10000
            weather.nebulosity = self.get_nebulosity(data['weather'][0]['icon'])
            weather.save()

            weather_hour = WeatherTempHour(temp=weather.temp, mm=weather.mm, time=datetime.datetime.now(), place=0,
                                           city=city_id)
            weather_hour.save()

        WeatherTempHour.objects.filter(time__lte=datetime.datetime.now() - datetime.timedelta(hours=48)).delete()

    def detailed(self):
        """Граббер прогноза погоды на 5 дней"""

        def basic_set(weather, forecast):
            """Устанавливает набор общих свойств для прогноза погоды"""

            weather.datetime = forecast['date'].replace(hour=weather.hour)
            weather.day = forecast['date'].day
            weather.temp_from = forecast['t']
            weather.temp_to = forecast['t']
            weather.mm = forecast['mm']
            weather.wind = forecast['wind']
            weather.wind_t = forecast['wind_t']
            weather.humidity = forecast['humidity']
            weather.nebulosity = forecast['nebulosity']
            weather.precipitation = forecast['precipitation']

            if weather.mm:
                weather.mm = int(weather.mm * 0.9464)

            return weather

        def additional_set(weather, forecast):
            weather.temp_to = forecast['t']

            return weather

        for city_id, owp_id in WEATHER_CITY_ID_MAP.items():
            data = self.send_request(WEATHER_3HOUR_URL, owp_id)

            if not data:
                continue

            # Часы прогнозоы OWM не соответствуют нашим.
            # Утро: 5-8 часов (берем за 6 часов)
            # День: 11-14 часов (берем за 12 часов)
            # Вечер: 17-20 часов (берем за 18 часов)
            # Ночь: 23-02 часов (берем за 21 час)

            forecasts = []
            for forecast in data['list']:
                date = datetime.datetime.fromtimestamp(forecast['dt'])
                # 2 часа ночи относим к предидущему дню
                if date.hour == 2:
                    date = date - datetime.timedelta(1)

                forecasts.append({
                    'date': date,
                    't': int_or_none(forecast['main']['temp']),
                    'mm': self.pressure_hpa_to_mm(forecast['main']['pressure']),
                    'wind': int_or_none(round(forecast['wind']['speed'])),
                    'wind_t': self.wind_degree_convent(forecast['wind']['deg']),
                    'humidity': int_or_none(forecast['main']['humidity']),
                    'nebulosity': self.get_nebulosity(forecast['weather'][0]['icon']),
                    'precipitation': self.get_precipitation(forecast['weather'][0]['id']),
                })

            for date in sorted(list(set([x['date'].date() for x in forecasts])), reverse=True):
                WeatherDetailed.objects.filter(city_id=city_id, datetime__year=date.year, datetime__month=date.month,
                                               datetime__day=date.day).delete()

                morning = WeatherDetailed(city_id=city_id, hour=6)
                day = WeatherDetailed(city_id=city_id, hour=12)
                evening = WeatherDetailed(city_id=city_id, hour=18)
                night = WeatherDetailed(city_id=city_id, hour=21)

                for forecast in forecasts:

                    dt = forecast['date']
                    if dt.date() == date:
                        if dt.hour == 5:
                            morning = basic_set(morning, forecast)
                        elif dt.hour == 8:
                            morning = additional_set(morning, forecast)
                        elif dt.hour == 11:
                            day = basic_set(day, forecast)
                        elif dt.hour == 14:
                            day = additional_set(day, forecast)
                        elif dt.hour == 17:
                            evening = basic_set(evening, forecast)
                        elif dt.hour == 20:
                            evening = additional_set(evening, forecast)
                        elif dt.hour == 23:
                            night = basic_set(night, forecast)
                        elif dt.hour == 2:
                            night = additional_set(night, forecast)

                # Если у модели нет заполненного datetime, считаем, что ее данные в принципе не были заполнены
                if morning.datetime:
                    morning.save()
                if day.datetime:
                    day.save()
                if evening.datetime:
                    evening.save()
                if night.datetime:
                    night.save()

                # Заполнение краткого прогноза
                if day.datetime:

                    # Определение восхода и заката солнца
                    coord = data['city']['coord']
                    obs = ephem.Observer()
                    sun = ephem.Sun()
                    obs.lon = str(coord['lon'])
                    obs.lat = str(coord['lat'])
                    obs.elevation = 440
                    date = datetime.datetime(date.year, date.month, date.day, hour=12)
                    sun_v = obs.previous_rising(sun).datetime() + datetime.timedelta(hours=8)
                    sun_z = obs.next_setting(sun).datetime() + datetime.timedelta(hours=8)

                    WeatherCities.objects.update_or_create(
                        city_id=city_id, source=0, date=date, defaults={
                            'day': day.temp_from,
                            'wind': day.wind,
                            'wind_t': day.wind_t,
                            'sun_v': sun_v,
                            'sun_z': sun_z,
                            'nebulosity': day.nebulosity,
                            'precipitation': day.precipitation,
                            'stamp': datetime.datetime.now(),
                        })
                if night.datetime:
                    WeatherCities.objects.update_or_create(
                        city_id=city_id, source=0, date=date, defaults={
                            'night': night.temp_to,
                            'stamp': datetime.datetime.now(),
                        })
