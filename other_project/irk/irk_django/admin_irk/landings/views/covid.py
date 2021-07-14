# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import Http404

from irk.landings.models import CovidPage
from irk.news.models import Block


def index(request):
    """
    Лендинг с новостями по коронавирусу
    """
    covid_page = CovidPage.objects.get(slug='main')
    context = {'page': covid_page}

    if request.is_ajax():
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1

        cards = covid_page.cards.filter(visible=True).order_by('-created', '-id')
        paginator = Paginator(cards, 20)
        try:
            context['cards'] = paginator.page(page)
        except (EmptyPage, InvalidPage):
            raise Http404()

        return render(request, 'landings/covid/cards_list.html', context)

    # Получить материалы для зафиксированых карточек COVID
    fixed_materials = []
    block = Block.objects.filter(slug='landings_covid_fixed_cards').first()
    if block:
        for position in block.positions.all():
            if not position.material or position.material.is_hidden:
                continue
            fixed_materials.append(position.material)
        context['fixed_materials'] = fixed_materials

    return render(request, 'landings/covid/index.html', context)
