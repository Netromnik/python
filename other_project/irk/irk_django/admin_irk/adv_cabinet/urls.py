# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import include, url

from irk.adv_cabinet import views

app_name = 'adv_cabinet'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^banners/$', views.banner_list, name='banners'),
    url(r'^banner/(?P<banner_id>[0-9]+)/$', views.banner_details, name='banner'),
    url(r'^companies/$', views.companies, name='companies'),
    url(r'^api/', include('irk.adv_cabinet.api.urls')),
]
