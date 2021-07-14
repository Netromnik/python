# -*- coding: utf-8 -*-

import os

from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.views import generic
from wsgiref.util import FileWrapper
from django.conf import settings

from irk.newyear2014.models import Wallpaper


class ListView(generic.ListView):
    model = Wallpaper
    template_name = 'newyear2014/wallpapers/index.html'
    queryset = Wallpaper.objects.all().order_by('-pk')

index = ListView.as_view()


def download(request, pk, size):
    wallpaper = get_object_or_404(Wallpaper, pk=pk)

    if size == 'standard':
        filename = str(wallpaper.standard_image)
    elif size == 'wide':
        filename = str(wallpaper.wide_image)
    else:
        raise Http404()

    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    _, ext = os.path.splitext(filepath)
    wrapper = FileWrapper(open(filepath))
    response = HttpResponse(wrapper, content_type='image/jpeg')
    response['Content-Length'] = os.path.getsize(filepath)
    response['Content-Disposition'] = "attachment; filename=irkru_2014_%s_%s%s" % (size, pk, ext)
    return response
