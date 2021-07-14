# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.ratings import views

app_name = 'ratings'

urlpatterns = [
    url(r'^$', views.rate, name='rate'),
]
