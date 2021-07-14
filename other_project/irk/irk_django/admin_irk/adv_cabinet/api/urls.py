# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url

from irk.adv_cabinet.api import views

urlpatterns = [
    url(r'^banners/$', views.BannerListAPIView.as_view(), name='api.banners'),
    url(r'^banner/(?P<pk>[0-9]+)/$', views.LogListAPIView.as_view(), name='api.banner'),
]
