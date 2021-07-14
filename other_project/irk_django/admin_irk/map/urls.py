# -*- coding: utf-8 -*-

from django.conf.urls import include, url

urlpatterns = [
    url(r'^map/', include('irk.map.api.urls')),
]
