# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta

from pytils import dt
from pytils.templatetags import init_defaults

from django import template, conf

register = template.Library()


@register.filter
def ru_strftime_flat(date, format=u"%d.%m.%Y", inflected_day=False, preposition=False):
    """
    Дополнение к pytils.dt - фильтр, форматирующий дату без склонения месяца.
    inflected=False, inflected_day=False, preposition=False
    """

    debug = conf.settings.DEBUG  #: Debug mode (sets in Django project's settings)
    show_value = getattr(conf.settings, 'PYTILS_SHOW_VALUES_ON_ERROR', False)  #: Show values on errors (sets in Django project's settings)
    default_value, default_uvalue = init_defaults(debug, show_value)

    try:
        res = dt.ru_strftime(format,
                             date,
                             inflected=False,
                             inflected_day=inflected_day,
                             preposition=preposition)
    except Exception as err:
        # because filter must die silently
        try:
            default_date = date.strftime(format)
        except Exception:
            default_date = str(date)
        res = default_value % {'error': err, 'value': default_date}
    return res


@register.filter
def dates(value, formats):
    """Форматирование даты в зависимости от ее года

    Примеры использования::
        object.created|dates:'d.m|d.m.Y'
    """
    try:
        current, old = formats.split('|')
        if value.year == date.today().year:
            return dt.ru_strftime(date=value, format=unicode(current), inflected=True)
        return dt.ru_strftime(date=value, format=unicode(old), inflected=True)
    except (AttributeError, TypeError, ValueError):
        return ''

@register.filter
def number_to_weekday_name(value, format_='full'):
    """ Возвращает название дня недели по его номеру начиная с 0 согласно формату

    Вид форматов:
    short: "пн"
    full: "понедельник"

    Примеры использования::
        weekday_number|number_to_weekday_name:'short'
    """

    if format_ == 'short':
        return dt.DAY_NAMES[value][0]
    else:
        return dt.DAY_NAMES[value][1]


@register.filter
def pretty_date(dtime, format='short'):
    """Вывод времени общего в красивом виде

    Вид форматов:
    short: "сегодня", "вчера", "25 сентября", "25 сентября 2013"
    full: "менее минуты назад", "5 минут назад", "5 часов назад", "вчера", "позавчера", "25.09", "25.09.13"
    """

    now = datetime.now()

    if format == 'short':
        if dtime.date() == now.date():
            return u'сегодня'
        if now + timedelta(1) <= dtime + timedelta(2) <= now + timedelta(2):
            return u'вчера'
        if dtime.year == now.year:
            return dt.ru_strftime(date=dtime, format=u'%d %B', inflected=True)
        return dt.ru_strftime(date=dtime, format=u'%d %B %Y', inflected=True)
    if format == 'full':
        if dtime + timedelta(3) > now:
            return dt.distance_of_time_in_words(dtime, accuracy=1)
        if dtime.year == now.year:
            return dt.ru_strftime(date=dtime, format=u'%d.%m', inflected=True)
        return dt.ru_strftime(date=dtime, format=u'%d.%m.%Y', inflected=True)


@register.filter
def datetime_from_timestamp(value):
    """Получить объект datetime из unix timestamp"""

    try:
        result = datetime.fromtimestamp(int(value))
    except Exception:
        return ''

    return result
