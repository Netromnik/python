# -*- coding: utf-8 -*-

import random
from itertools import chain

import chardet
import six
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from django.shortcuts import render

from irk.news.views.base.list import NewsListBaseView
from irk.tourism.helpers import split_by_column
from irk.tourism.models import Place, Tour, Hotel, TourBase, TourFirm, Article


class ArticleAjaxListView(NewsListBaseView):
    model = Article
    template = 'tourism/index.html'
    ajax_template = 'tourism/article/article_list.html'
    pagination_limit = 4

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.ajax_get(request, *args, **kwargs)

        return super(ArticleAjaxListView, self).dispatch(request, *args, **kwargs)

    def ajax_get(self, request, *args, **kwargs):
        context = self._make_context()
        return render(request, self.ajax_template, context)

    def extra_context(self, request, queryset, extra_params=None):
        context = super(ArticleAjaxListView, self).extra_context(request, queryset, extra_params)
        context['is_moderator'] = self.show_hidden(request)

        if not request.is_ajax():
            places = list(Place.objects.filter(is_main=True).prefetch_related('parent'))
            place_local = split_by_column(sorted(filter(lambda x: x.type in (0, 2), places), key=lambda x: x.title))
            places_foreign = split_by_column(sorted(filter(lambda x: x.type == 1, places), key=lambda x: x.title))

            context['places_local'] = place_local
            context['places_foreign'] = places_foreign
            context['news_index'] = True

        return context


index = ArticleAjaxListView.as_view()


def global_search(request):
    """Поиск по всем объектам туризма"""

    type = request.GET.get('type') if request.GET.get('type') else 'tour'
    q = request.GET.get('q')
    if q and isinstance(q, six.binary_type):
        encoding = chardet.detect(q)['encoding']
        if encoding and encoding not in ('utf-8', 'ascii'):
            q = q.decode(encoding).encode('utf-8')

    random_place = None
    random_firm = None
    random_tour = None

    if not q:
        objects = None
    else:
        if type == 'place':
            queryset = Place.objects.filter(title__icontains=q).order_by('title')
        elif type == 'firm':
            # TODO: объединить в один запрос
            hotel_queryset = Hotel.search.query({'q': q})
            tourbase_queryset = TourBase.search.query({'q': q})
            tourfirm_queryset = TourFirm.search.query({'q': q})
            queryset = sorted(chain(hotel_queryset, tourbase_queryset, tourfirm_queryset), key=lambda x: x.name)

            places = Place.objects.filter(title__icontains=q)
            try:
                random_place = places[random.randrange(0, places.count())]
            except (IndexError, ValueError):
                random_place = None

            tours_ids = list(Tour.objects.filter(is_hidden=False).filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(place__title__icontains=q)).extra(select={
                'date': "SELECT `date` FROM `tourism_tour_periods` WHERE `tourism_tour_periods`.`tour_id` = `tourism_tours`.`id` AND `tourism_tour_periods`.`date` >= NOW() ORDER BY `tourism_tour_periods`.`date` ASC LIMIT 0, 1"
            }).values_list('id', flat=True))

            try:
                random_tour = Tour.objects.get(pk=random.choice(tours_ids))
            except (IndexError, ValueError):
                random_tour = None

        else:
            queryset = Tour.objects.filter(is_hidden=False).filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(place__title__icontains=q)).extra(select={
                'date': "SELECT `date` FROM `tourism_tour_periods` WHERE `tourism_tour_periods`.`tour_id` = `tourism_tours`.`id` AND `tourism_tour_periods`.`date` >= NOW() ORDER BY `tourism_tour_periods`.`date` ASC LIMIT 0, 1"
            })

            places = Place.objects.filter(title__icontains=q)

            if places.count():
                random_place = places[random.randrange(0, places.count())]
            else:
                random_place = None

            hotel_queryset = Hotel.objects.filter(name__icontains=q, visible=True, is_active=True)
            tourbase_queryset = TourBase.objects.filter(name__icontains=q, visible=True, is_active=True)
            tourfirm_queryset = TourFirm.objects.filter(name__icontains=q, visible=True, is_active=True)
            firms = list(hotel_queryset) + list(tourbase_queryset) + list(tourfirm_queryset)
            try:
                random_firm = firms[random.randrange(0, len(firms))]
            except (IndexError, ValueError):
                random_firm = None

        try:
            page = int(request.GET.get('page'))
        except (TypeError, ValueError):
            page = 0

        paginate = Paginator(queryset, 20)

        try:
            objects = paginate.page(page)
        except (EmptyPage, InvalidPage):
            objects = paginate.page(1)

    context = {
        'random_place': random_place,
        'random_firm': random_firm,
        'random_tour': random_tour,
        'objects': objects,
        'q': q,
        'type': type,
        'search_type': type,  # Для `tourism/base/search.html`
    }

    return render(request, 'tourism/search_result.html', context)


def hotel_order(request):
    """Заказ отелей"""

    return render(request, 'tourism/hotel/order.html')


def aviasales(request):
    """Купить авиабилет на aviasales.ru"""

    return render(request, 'tourism/aviasales.html')
