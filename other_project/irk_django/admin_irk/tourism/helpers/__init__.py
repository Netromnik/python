# -*- coding: utf-8 -*-

import random
import datetime
import string
from math import ceil, floor

from django.core.exceptions import ObjectDoesNotExist


def split_by_column(places, column_count=3):
    """ Разделяем массив на колонки, выравнивая количество элеменов """

    float_line_in_column = len(places) / float(column_count)
    min_line_in_column = floor(float_line_in_column)
    max_line_in_column = ceil(float_line_in_column)
    difference = len(places) - column_count * min_line_in_column
    columns = [[]]
    i = 0
    line_count = 0
    for place in places:
        line_count += 1
        if line_count > min_line_in_column:
            if difference > 0 and line_count <= max_line_in_column:
                difference -= 1
            else:
                i += 1
                line_count = 1
                columns.append([])
        columns[i].append(place)
    return columns


def convent_place_type(value):
    """ Преревод алиас типа места отдыха в его ид и наоборот """

    from irk.tourism.models import Place
    try:
        try:
            return Place.TYPES_SLUG[int(value)]
        except ValueError:
            result = dict((v,k) for k,v in Place.TYPES_SLUG.items())
            return result[value]
    except KeyError:
        pass
    return False

   
def parse_date(text):
    """Разбиение строки дат на отдельные даты

    10.05.2010,11.05.2010, 14.05.2010-17.05.2010,18.05.2010,30.12.2010-5.1.2011"""

    parts = [x for x in map(string.strip, text.split(',')) if x]
    res = []
    for part in parts:
        try:
            date = datetime.datetime.strptime(part, '%d.%m.%Y').date()
            res.append(date)
        except ValueError, e:
            try:
                start, end = part.split('-')
                start = datetime.datetime.strptime(start, '%d.%m.%Y').date()
                end = datetime.datetime.strptime(end, '%d.%m.%Y').date()
                days = end - start
                res += [start + datetime.timedelta(days=x) for x in range(0, days.days + 1)]
            except Exception:
                continue

    return res


def date_periods(dates):
    dates = list(set(dates))
    dates.sort()
    res = []
    for date in dates:
        idx = dates.index(date)
        rng = []
        start_date = date
        for next_date in dates[idx+1:]:
            dim = next_date - date
            if dim.days == 1:
                date = next_date
                rng.append(next_date)
            else:
                break
        if rng:
            for date in rng:
                dates.remove(date)
            rng.sort()
            res.append((start_date, rng[-1]))
        else:
            res.append((start_date,))
    return res
 
def join_date(dates):
    '''Объединение списка дат в строку'''
    return ', '.join(map( lambda x : '-'.join(map(lambda y: y.strftime("%d.%m.%Y"),x)) ,date_periods(dates)))

def columns_split(queryset, items=6):
    """Разбиваем список мест отдыха на колонки для рубрикатора"""    

    letters = [unichr(x) for x in range(ord(u'а'), ord(u'я')+1)]
    each = 6

    columns = []
    idx = 0
    for i in range(0, 6):
        current_letters = letters[idx*each:each*idx+each]
        idx += 1
        data = {'places': [], 'letters': current_letters}
        matches = filter(lambda x: x.title[0].lower() in current_letters, queryset)
        if matches:
            data['places'] = matches
            columns.append(data)
    return columns

def link_firm(firm, section):
    """Привязка фирмы phones.models.Firms к моделям туризма"""

    from irk.tourism.models import TourismFirm

    Model = section.content_type.model_class()

    try:
        tourism_firm = TourismFirm.objects.get(firm=firm)
    except TourismFirm.DoesNotExist:
        tourism_firm = TourismFirm(firm=firm)
        tourism_firm.save()

    try:
        linked_firm = Model.objects.get(tourismfirm_ptr=tourism_firm)
    except Model.DoesNotExist:
        linked_firm = Model()
        linked_firm.tourismfirm_ptr = tourism_firm
        linked_firm.firm = tourism_firm.firm
        linked_firm.place = tourism_firm.place
        linked_firm.price = tourism_firm.price or ''
        linked_firm.price_comment = tourism_firm.price_comment
        linked_firm.logo = tourism_firm.logo
        linked_firm.promo = tourism_firm.promo
        # linked_firm.save()

    if section.slug == 'hotel':
        linked_firm.visible = firm.visible

    if not linked_firm.price:
        linked_firm.price = ''
    linked_firm.save()

    return linked_firm

def get_linked_firm(firm):
    """Получение фирмы туризма по имеющейся фирме `phones.models.Firms'"""

    from irk.tourism.models import Hotel, TourBase, TourFirm

    for model in (Hotel, TourBase, TourFirm):
        try:
            return model.objects.get(pk=firm.pk)
        except model.DoesNotExist:
            continue

    raise ObjectDoesNotExist()