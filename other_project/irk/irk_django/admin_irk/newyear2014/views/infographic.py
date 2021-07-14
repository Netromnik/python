# -*- coding: utf-8 -*-

from django.views import generic

from irk.newyear2014.models import Infographic
from irk.newyear2014.permissions import is_moderator


class Mixin(object):

    def get_queryset(self):
        infographics = Infographic.objects.filter(sites=self.request.csite).order_by('-stamp')
        moderator = is_moderator(self.request.user)
        if not moderator:
            infographics = infographics.filter(is_hidden=False)

        return infographics


class ListView(Mixin, generic.ListView):
    model = Infographic
    template_name = 'newyear2014/infographic/index.html'

index = ListView.as_view()


class DetailView(Mixin, generic.DetailView):
    model = Infographic
    template_name = 'newyear2014/infographic/read.html'

read = DetailView.as_view()
