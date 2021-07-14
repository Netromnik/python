# -*- coding: UTF-8 -*-
from django.shortcuts import render


def index(request):
    """Индекс ice climber"""

    return render(request, 'newyear2014/climber/index.html')