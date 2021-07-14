# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.map.api import views

urlpatterns = [
    url(r'^city/$', views.city_list, name='map.api.city.list'),
    url(r'^city/(?P<pk>\d+)/$', views.city_instance, name='map.api.city.instance'),
    url(r'^autocomplete/countryside/$', views.autocomplete_countryside, name='map.api.autocomplete.countryside'),
    url(r'^autocomplete/cooperative/$', views.autocomplete_cooperative, name='map.api.autocomplete.cooperative'),
]
