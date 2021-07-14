# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404

from irk.newyear2014.models import Puzzle


def index(request):

    puzzles = Puzzle.objects.all()

    context = {
        'objects': puzzles
    }

    return render(request, 'newyear2014/puzzle/index.html', context)
