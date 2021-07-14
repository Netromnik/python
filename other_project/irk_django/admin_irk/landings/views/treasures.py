# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.shortcuts import render

from irk.landings.models import TreasureDish
from irk.options.models import Site
from irk.utils.http import JsonResponse


def index(request, lang=None):
    """Гастрономическая карта"""

    # первые добавленные блюда - без категории
    dishes = TreasureDish.objects.filter(is_visible=True, category__isnull=True) \
                 .order_by('position')
    sites = Site.objects.filter(is_hidden=False, in_menu=True).order_by('position')

    context = {
        'dishes': dishes,
        'sites': sites,
        'en': True if lang == 'en' else False,
    }

    return render(request, 'landings/treasures.html', context)


def gidsiberia(request, lang=None):
    """Гастрономическая карта v2"""

    dishes = TreasureDish.objects.filter(is_visible=True) \
        .filter(category__slug='v2') \
        .order_by('position')

    establishments = []

    for dish in dishes:
        if dish.establishment not in establishments:
            establishments.append(dish.establishment)

    sites = Site.objects.filter(is_hidden=False, in_menu=True).order_by('position')

    context = {
        'establishments': establishments,
        'sites': sites,
        'en': True if lang == 'en' else False,
    }

    return render(request, 'landings/gidsiberia.html', context)


def points(request, v2=False):
    """Точки для яндекс карт"""

    dishes = TreasureDish.objects.filter(is_visible=True)
    if v2:
        dishes = dishes.filter(category__slug='v2')
    else:
        dishes = dishes.filter(category__slug__isnull=True)

    data = {
        'type': 'FeatureCollection',
        'features': []
    }

    for dish in dishes:
        establishment = dish.establishment
        lat = lon = None
        if establishment.point:
            lat, lon = [float(x) for x in establishment.point.split(',')]

        data['features'].append({
            'type': 'Feature',
            'id': dish.pk,
            'establishment_id': dish.establishment_id,
            'geometry': {
                'type': 'Point',
                'coordinates': [lat, lon],
            },
            'properties': {
                'iconCaption': establishment.name
            }
        })

    return JsonResponse(data)
