# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.http import HttpResponse


def index(request):
    return HttpResponse('API. Use the token, fool.')


urlpatterns = [
    url(r'^news/', include('irk.news.api.urls')),
    url(r'^map/', include('irk.map.api.urls')),
    url(r'^statistic/', include('irk.statistic.api.urls')),
]
