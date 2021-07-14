# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.shortcuts import render

from irk.landings.models import Article9May
from irk.utils.http import JsonResponse


def index(request):
    """
    Карта памятных мест в Иркутске в честь дня победы 9 мая 2020 года
    """
    articles = Article9May.objects.filter(is_hidden=False)
    context = {'articles': articles}

    return render(request, 'landings/victory2020/index.html', context)


def points(request):
    """Точки для яндекс карт"""

    materials = Article9May.objects.filter(is_hidden=False)

    data = {
        'type': 'FeatureCollection',
        'features': []
    }

    for material in materials:
        lat = lon = None

        if material.point:
            lat = material.point.x
            lon = material.point.y

        data['features'].append({
            'type': 'Feature',
            'id': material.pk,
            'address': material.address,
            'geometry': {
                'type': 'Point',
                'coordinates': [lat, lon],
            },
        })

    return JsonResponse(data)
