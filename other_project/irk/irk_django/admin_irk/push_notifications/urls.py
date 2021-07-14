# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.push_notifications import views

app_name = 'push_notifications'

urlpatterns = [
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
    url(r'^unsubscribe/$', views.unsubscribe, name='unsubscribe')
]
