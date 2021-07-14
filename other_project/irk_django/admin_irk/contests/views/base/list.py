# -*- coding: utf-8 -*-

"""Class-based view для списка конкурсов"""

import datetime

from django.views.generic.list import ListView

from irk.contests.models import Contest
from irk.news.permissions import can_see_hidden


class ListContestBaseView(ListView):
    model = Contest
    paginate_by = 10
    by_csite = True  # Учитывать в выборке csite. Конкурс открыт не из раздела конкурсов

    def get_queryset(self, *args, **kwargs):
        queryset = super(ListContestBaseView, self).get_queryset()
        today = datetime.date.today()
        queryset = queryset.filter(date_end__lt=today).order_by('-date_start')

        if not can_see_hidden(self.request.user):
            queryset = queryset.filter(is_hidden=False)

        if self.by_csite:
            queryset = queryset.filter(sites=self.request.csite)
        else:
            # HACK: пока шаблоны только для обеда
            queryset = queryset.filter(vote_type=Contest.SITE_VOTE)

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(ListContestBaseView, self).get_context_data(**kwargs)
        today = datetime.date.today()
        opened = self.model.objects.filter(date_start__lte=today, date_end__gte=today).order_by('-date_start')

        if not can_see_hidden(self.request.user):
            opened = opened.filter(is_hidden=False)

        if self.by_csite:
            opened = opened.filter(sites=self.request.csite)
        else:
            # HACK: пока шаблоны только для обеда
            opened = opened.filter(vote_type=Contest.SITE_VOTE)

        context['opened'] = opened[:10]
        context['closed'] = context['object_list']

        return context


contests_list = ListContestBaseView.as_view()
