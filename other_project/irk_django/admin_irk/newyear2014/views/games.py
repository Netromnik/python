# -*- coding: UTF-8 -*-
from django.shortcuts import render


def index(request):
    """Индекс игр"""

    return render(request, 'newyear2014/games.html')