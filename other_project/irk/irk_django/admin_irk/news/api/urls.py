# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.news.api import views, sms

urlpatterns = [
    url(r'^sms/receive/$', sms.flash_create, name='api.sms.create'),
    url(r'^$', views.news_list, name='api.news.list'),
    url(r'^(?P<pk>\d+)/$', views.news_read, name='api.news.instance'),
]
