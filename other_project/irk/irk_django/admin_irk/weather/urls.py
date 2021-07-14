# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.http import HttpResponseGone

from irk.weather import views

app_name = 'weather'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^graph/', HttpResponseGone, name='graph'),
    url(r'^charts/(?P<city_id>\d+)/$', views.charts, name='charts'),
    url(r'^map_forecasts/$', views.map_forecasts, name='map_forecasts'),
    url(r'^map_detailed/$', views.map_detailed, name='map_detailed'),
    url(r'^detailed/(?P<city_id>\d+)/$', views.detailed, name='detailed'),
    url(r'^instagram/', views.weather_instagram, name='instagram_posts'),
    url(r'^moon-day/$', views.moon_calendar, name='moon_day'),
    url(r'^sudoku/$', views.sudoku_page, name='sudoku'),
    url(r'^(?P<city_alias>[\w/-]+)/detailed/$', HttpResponseGone),
]
