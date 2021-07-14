# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url

from irk.game import views

app_name = 'game'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^found/(?P<treasure_id>\d+)/(?P<hash_>[\w\d]+)/$', views.FoundView.as_view(), name='found'),
    url(r'^purchase/(?P<prize_id>\d+)/$', views.PurchaseView.as_view(), name='purchase'),
]
