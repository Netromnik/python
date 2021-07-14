# -*- coding: utf-8 -*-

import datetime

from django.shortcuts import render, get_object_or_404

from irk.newyear2014.models import Offer


def index(request):
    today = datetime.date.today()
    offers = Offer.objects.filter(date_start__lte=today, date_end__gte=today)

    context = {
        'objects': offers,
    }

    return render(request, 'newyear2014/offers/index.html', context)


def read(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id)

    context = {
        'object': offer,
    }

    return render(request, 'newyear2014/offers/read.html', context)
