# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.http import Http404
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from irk.landings.models import Thank
from irk.landings.forms import ThankForm


def index(request):
    """
    Благодарность докторам
    """

    limit = 10

    thanks = Thank.objects.filter(is_visible=True).order_by('-created')

    paginator = Paginator(thanks, limit)
    page = paginator.page(1)

    # Добавление благодарности
    if request.is_ajax() and request.POST:
        form = ThankForm(data=request.POST)
        if form.is_valid():
            form.save()
    # Аяксовая подгрузка списка благодарностей
    elif request.is_ajax():
        try:
            page = int(request.GET.get('page', 2))
        except ValueError:
            raise Http404()

        paginator = Paginator(thanks, limit)
        try:
            page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            raise Http404()

        context = {'thanks': page.object_list}

        return render(request, 'landings/thanks/cards_list.html', context)
    else:
        form = ThankForm()

    context = {
        'thanks': page.object_list,
        'form': form,
    }

    return render(request, 'landings/thanks/index.html', context)
