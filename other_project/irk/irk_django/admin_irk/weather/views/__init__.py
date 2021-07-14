# -*- coding: utf-8 -*-

import datetime

from django.http import Http404
from django.shortcuts import render
from django.template.loader import render_to_string

from irk.map.models import Cities
from irk.utils.http import ajax_request
from irk.utils.helpers import int_or_none, get_object_or_none

from irk.weather import user_options
from irk.weather.controllers import WeatherInstagramController, WishController
from irk.weather.forecasts import ForecastCurrent, ForecastByDays, ForecastMapCities, ForecastDetailed, ForecastDay
from irk.weather.helpers import get_moon_phase
from irk.weather.models import MeteoCentre, FirePlace, WeatherSigns, WeatherTempHour, MoonTiming, MoonDay, Joke


def index(request):
    """Главная страница погоды"""

    # Текущее время
    now = datetime.datetime.now()

    city = user_options.WeatherFavoriteCity(request).value
    if not city:
        city = request.csite.cities_set.get(alias='irkutsk')

    forecast_current = ForecastCurrent(city, now)
    forecast_by_days = ForecastByDays(city, now.date()).get_forecasts()

    meteocentre = MeteoCentre.objects.filter(stamp=now.date()).first()
    sign = WeatherSigns.objects.filter(month=now.month, day=now.day).first()
    joke = Joke.objects.filter(month=now.month, day=now.day).first()
    fireplaces_coords = [x.coords for x in FirePlace.objects.values_list('center', flat=True)]
    fireplaces_updated = FirePlace.objects.order_by('created').values_list('created', flat=True).last()

    forecast_day = ForecastDay(city, now)
    wisher = WishController(forecast_day, meteocentre)
    wish = wisher.get_wish()

    context = {
        'now': now,
        'wish': wish,
        'city': city,
        'forecast': forecast_current,
        'forecast_by_days': forecast_by_days,
        'meteocentre': meteocentre,
        'sign': sign,
        'joke': joke,
        'fireplaces': {
            'places': fireplaces_coords,
            'updated': fireplaces_updated,
        },
    }

    return render(request, 'weather/index.html', context)


def moon_calendar(request):
    """Лунный календарь"""

    now = datetime.datetime.now()
    moon_day_number = MoonTiming.moon_day_number(now)
    moon_day = MoonDay.objects.filter(number=moon_day_number).first()
    if not moon_day:
        raise Http404('Moon day does not exist')

    moon_phase = get_moon_phase(now)

    return render(request, 'weather/moon_day.html', {
        'moon_day': moon_day,
        'moon_phase': moon_phase,
    })


def sudoku_page(request):
    """Судоку"""

    return render(request, 'weather/sudoku.html')


@ajax_request
def detailed(request, city_id):
    """Детальный прогноз погоды по городу"""

    city = get_object_or_none(Cities, id=city_id)
    if not city:
        return {'ok': False, 'msg': u'Does not exists city with id {}'.format(city_id)}

    start_date = datetime.datetime.now()

    forecasts_by_days = ForecastDetailed(city, start_date).get_forecasts()

    context = {
        'forecasts_by_days': forecasts_by_days,
        'request': request,
        'city': city,
    }

    return {
        'ok': True,
        'html': render_to_string('weather/snippets/weather_detailed.html', context)
    }


@ajax_request
def weather_instagram(request):
    """Ajax-подгрузка постов инстаграма про погоду"""

    start = int_or_none(request.GET.get('start')) or 0
    limit = int_or_none(request.GET.get('limit')) or 4

    ctrl = WeatherInstagramController()
    posts, page_info = ctrl.get_posts(start, limit)

    result = {
        'ok': True,
        'html': render_to_string('weather/tags/weather_instagram_list.html', {'posts': posts}),
        'page_info': page_info,
    }
    # Поддержка старой версии пагинатора на клиенте.
    result.update(page_info)

    return result


@ajax_request
def charts(request, city_id):
    """Графики давления и температуру для города за день"""

    city = get_object_or_none(Cities, id=city_id)
    if not city:
        return {'ok': False, 'msg': u'Does not exists city with id {}'.format(city_id)}

    start_date = datetime.datetime.now() - datetime.timedelta(days=1)

    queryset = WeatherTempHour.objects.filter(time__gte=start_date, city=city.id).order_by('time')

    points = []
    seen_hours = set()
    for point in queryset:
        if point.time.hour not in seen_hours:
            seen_hours.add(point.time.hour)
            points.append({
                'datetime': point.time.strftime('%d-%m-%y %H-%M'),
                'pressure': point.mm,
                'temperature': point.temp,
            })

    return {
        'ok': True,
        'points': points,
    }


@ajax_request
def map_forecasts(request):
    """Карта прогнозов погоды"""

    stamp = datetime.datetime.now()
    forecasts = ForecastMapCities(stamp).get_forecasts()

    return {
        'ok': True,
        'forecasts': list(forecasts),
    }


@ajax_request
def map_detailed(request):
    """Детальный прогноз погоды по городу на карте"""

    city_id = request.GET.get('city_id')
    if not city_id:
        return {'ok': False, 'msg': u'Нет обязательного параметра'}

    city = get_object_or_none(Cities, id=city_id)
    if not city:
        return {'ok': False, 'msg': u'Нет города с таким id: {}'.format(city_id)}

    stamp = datetime.datetime.now()

    context = {
        'city': city,
        'forecast_current': ForecastCurrent(city, stamp),
        'forecast_by_days': ForecastByDays(city, stamp.date()).get_forecasts(),
    }

    return {
        'ok': True,
        'html': render_to_string('weather/snippets/map_city_detailed.html', context)
    }
