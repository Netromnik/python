# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.utils.views import racinggame

app_name = 'racinggame'

urlpatterns = [
    url(r'^$', racinggame.index, name='index'),
    url(r'record/$', racinggame.save_record, name='save_record'),
    url(r'delete/(?P<username>[-\w]+)/$', racinggame.delete_from_top, name='delete_from_top'),
]
