# -*- coding: utf-8 -*-

import datetime

from django import template
from irk.tourism.models import Place


register = template.Library()

# Определение зимнего/летнего сезона
WINTER_SEASON = [(11, 15), (3, 15)]  # с 15 ноября по 15 марта
SUMMER_SEASON = [(4, 25), (10, 15)]  # с 25 авреля пл 15 октября


def date_in_period(date, period):
    """ Проверяет входит ли дата в период """

    year = date.year
    day = date.day

    # Обработка високосного года
    if date.month == 2 and date.day == 29:
        day = 28

    if period[0][0] < period[1][0]:
        start_date = datetime.date(year, period[0][0], period[0][1])
        end_date = datetime.date(year, period[1][0], period[1][1])
        date = datetime.date(year, date.month, day)
    else:
        start_date = datetime.date(year, period[0][0], period[0][1])
        end_date = datetime.date(year + 1, period[1][0], period[1][1])
        date = datetime.date(year if date.month > period[1][0] else (year + 1), date.month, day)

    return (date > start_date) and (date < end_date)


@register.simple_tag(takes_context=True)
def get_seasons(context, is_summer_season_var, is_winter_season_var):
    """ Определение текущего сезона """

    date = datetime.date.today()
    context[is_winter_season_var] = date_in_period(date, WINTER_SEASON)
    context[is_summer_season_var] = not context[is_winter_season_var] and date_in_period(date, SUMMER_SEASON)

    return ''


class WeatherPlaces(template.Node):

    def __init__(self, variable):
        self.variable = variable

    def render(self, context):
        try:
            context[self.variable] = Place.objects.filter(weather_popular=True)
        except IndexError:
            context[self.variable] = None
        return ''


@register.inclusion_tag("tourism/tags/places_menu.html")
def places_menu(selected=''):
    """Меню выбора Байкал Россия Зарубеж"""

    return {
        'selected': selected,
    }
