# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic import DetailView, ListView

from irk.adwords.models import AdWord, CompanyNews
from irk.adwords.permissions import is_moderator


def index(request):
    """Список рекламных новостей"""

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20

    paginate = Paginator(AdWord.objects.all().order_by('-pk'), limit)

    try:
        objects = paginate.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginate.page(paginate.num_pages)

    context = {
        'page': page,
        'limit': limit,
        'objects': objects,
    }

    return render(request, 'adwords/index.html', context)


def read(request, adword_id):
    """Просмотр рекламной новости"""

    adword = get_object_or_404(AdWord, pk=adword_id)

    context = {
        'adword': adword,
    }

    return render(request, 'adwords/read.html', context)


class CompanyNewsMixin(object):
    def extra_filter(self, queryset):
        if not is_moderator(self.request.user):
            queryset = queryset.filter(
                is_hidden=False,
            ).distinct()
        return queryset


class CompanyNewsReadView(CompanyNewsMixin, DetailView):
    model = CompanyNews
    pk_url_kwarg = 'news_id'
    template_name = 'company_news/read.html'

    def get_queryset(self):
        qs = super(CompanyNewsReadView, self).get_queryset()
        qs = self.extra_filter(qs)
        return qs


company_news_read = CompanyNewsReadView.as_view()
