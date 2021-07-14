# -*- coding: utf-8 -*-

from django.shortcuts import render


def transport_etrains(request):
    """Расписание электричек"""

    return render(request, 'tourism/transport/etrains_online.html', {'etrains': True})


def transport_trains(request):
    """Расписание поездов"""

    return render(request, 'tourism/transport/trains_online.html', {'trains': True})


def air_board(request):
    """Онлайн-табло"""

    return render(request, 'tourism/air_board.html')
