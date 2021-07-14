# -*- coding: utf-8 -*-

import datetime

from operator import attrgetter
from django.views import generic

from irk.newyear2014.models import PhotoContest, TextContest


class ListView(generic.ListView):

    template_name = 'newyear2014/contests/index.html'

    def get_queryset(self):
        today = datetime.date.today()

        photo_contests = list(PhotoContest.objects.filter(date_start__lte=today, date_end__gte=today).order_by('id').extra(select={'model': '"photo"'}))
        text_contests = list(TextContest.objects.filter(date_start__lte=today, date_end__gte=today).order_by('id').extra(select={'model': '"text"'}))
        contests = photo_contests + text_contests
        return sorted(contests, key=attrgetter('id'))

index = ListView.as_view()
