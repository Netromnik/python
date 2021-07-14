# -*- coding: utf-8 -*-


from django.shortcuts import render, get_object_or_404

from irk.newyear2014.models import Zodiac, Horoscope


def index(request):
    horoscopes = Horoscope.objects.all().order_by('-position')

    context = {
        'objects': horoscopes,
    }

    return render(request, 'newyear2014/horoscope/index.html', context)


def read(request, horoscope_id):
    horoscope = get_object_or_404(Horoscope, pk=horoscope_id)

    context = {
        'object': horoscope,
    }

    return render(request, 'newyear2014/horoscope/read.html', context)


def zodiac_read(request, zodiac_id):
    zodiac = get_object_or_404(Zodiac, pk=zodiac_id)

    context = {
        'object': zodiac,
    }

    return render(request, 'newyear2014/horoscope/zodiac_read.html', context)
