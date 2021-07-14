# -*- coding: utf-8 -*-

import datetime
from copy import deepcopy

from django import template
from django.core.urlresolvers import reverse_lazy

from irk.weather.controllers import WeatherInstagramController
from irk.weather.models import WeatherSigns
from irk.weather.forecasts import ForecastCurrent
from irk.weather.user_options import WeatherFavoriteCity

register = template.Library()


@register.filter
def sign(value):
    """Если температура положительная, подрисовываем +"""

    try:
        value = int(value)
    except (ValueError, TypeError):
        return value

    if value > 0:
        value = '+%s' % value

    return str(value)


class WeatherSignNode(template.Node):
    def __init__(self, variable):
        self.variable = variable

    def render(self, context):
        now = datetime.date.today()
        try:
            context[self.variable] = WeatherSigns.objects.get(month=now.month, day=now.day).text
        except (WeatherSigns.DoesNotExist, AttributeError):
            return ''
        return ''


# TODO Не используется
@register.tag
def weather_sign(parser, token):
    """{% weather_sign as sign %}"""

    bits = token.split_contents()

    return WeatherSignNode(bits[2])


@register.inclusion_tag('weather/tags/weather_instagram_block.html', takes_context=True)
def weather_instagram_block(context, start=0, limit=5):
    """Лента инстаграмма про погоду"""

    ctrl = WeatherInstagramController()
    posts, page_info = ctrl.get_posts(start, limit)

    return {
        'posts': posts,
        'page_info': page_info,
        'request': context.get('request'),
    }


RUBRICATOR_ITEMS = [
    {'url': reverse_lazy('weather:index'), 'name': u'Прогноз погоды'},
    {'url': reverse_lazy('weather:sudoku'), 'name': u'Судоку'},
    {'url': reverse_lazy('weather:moon_day'), 'name': u'Лунный календарь'},
]


@register.inclusion_tag('weather/tags/rubricator.html', takes_context=True)
def weather_rubricator(context):
    """Рубрикатор раздела «Погода»"""

    request = context.get('request')
    path = request.path_info

    main_items = deepcopy(RUBRICATOR_ITEMS)
    for item in main_items:
        # выбрана конкретно эта страница
        item['is_current'] = item['url'] == path
        # активный пункт меню
        item['is_active'] = item['is_current']

    return {
        'main_items': main_items,
    }


@register.inclusion_tag('weather/tags/toolbar.html', takes_context=True)
def weather_toolbar(context):
    """Погода в тулбаре"""

    request = context.get('request')

    weather_city = WeatherFavoriteCity(request).value
    forecast = ForecastCurrent(weather_city, datetime.datetime.now())

    return {
        'city': weather_city,
        'forecast': forecast,
    }
