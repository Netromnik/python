# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.adwords import views

app_name = 'adwords'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<adword_id>\d+)/$', views.read, name='read'),
]
