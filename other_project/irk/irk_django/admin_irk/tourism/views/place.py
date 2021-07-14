# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from django.http import Http404

from irk.tourism.models import Place, Hotel, TourBase
from irk.tourism.helpers import convent_place_type
from irk.tourism.helpers.places import show_panorama


def places(request, type_slug=None):
    """Места отдыха"""

    if type_slug is None:
        type_slug = 'baikal'

    type = convent_place_type(type_slug)

    if type is False:
        raise Http404()

    places = Place.objects.filter(parent__isnull=True, type=type).order_by('title')

    if type == 1:
        # Разбиение и сортировка по первой букве
        alphabet = {}
        letter = ''
        for place in places:
            first_letter = place.title[0]
            if letter != first_letter:
                letter = first_letter
                alphabet[letter] = []
            alphabet[first_letter].append(place)
        alphabet = sorted(alphabet.iteritems())

        # Разбиение на нужное число столбцов
        column_count = 4
        line_in_column = round(places.count()/column_count)
        columns = [[]]
        i = 0
        column_sum = 0
        for letter, places in alphabet:
            if column_sum >= line_in_column and i < (column_count-1):
                i += 1
                column_sum = 0
                columns.append([])
            column_sum += len(places)
            columns[i].append((letter, places))
        places = columns

    context = {
        'objects': places,
        'type_slug': type_slug,
        'search_type': 'place',
    }

    return render(request, 'tourism/place/list.html', context)


def place(request, place_slug):
    """Просмотр категории мест отдыха и мест, принадлежащих к ней"""

    NUM_COLS = 4

    note = bool(request.GET.get('note'))
    place = get_object_or_404(Place, slug=place_slug)
    
    count_children = place.children.count()
    num_items_in_col = count_children / NUM_COLS + ((count_children % NUM_COLS != 0 and 1) or 0)

    tours = place.tour_set.filter(is_hidden=False)

    context = {
        'note': note,
        'place': place,
        'tours': tours,
        'num_items_in_col': num_items_in_col,
        'search_type': 'place',
        'show_panorama': show_panorama,
    }

    return render(request, 'tourism/place/read_parent.html', context)


def sub_place(request, parent_slug, place_slug):
    """Просмотр подкатегории места"""

    note = bool(request.GET.get('note'))
    place = get_object_or_404(Place, parent__slug=parent_slug, slug=place_slug)

    tourbases = TourBase.objects.filter(place=place)
    hotels = Hotel.objects.filter(place=place)
    tourbases = filter(lambda x: x.pk not in [h.pk for h in hotels], tourbases)
    hotels = filter(lambda x: x not in [t.pk for t in tourbases], hotels)
    tours = place.tour_set.filter(is_hidden=False)

    context = {
        'tourbases': tourbases,
        'note': note,
        'place': place,
        'hotels': hotels,
        'tours': tours,
        'search_type': 'place',
        'show_panorama': show_panorama,
    }

    return render(request, 'tourism/place/read.html', context)
