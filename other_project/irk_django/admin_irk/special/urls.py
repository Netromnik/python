# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from irk.special import views

app_name = 'special'


urlpatterns = [
    url(r'^$', views.project_list, name='project_list'),
    url(r'^sponsor/click/(?P<sponsor_id>\d+)/$', views.sponsor_click, name='sponsor_click'),
    url(r'^(?P<slug>[\w-]+)/$', views.index, name='index'),
]
