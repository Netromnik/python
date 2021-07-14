# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from irk.contests import views

app_name = 'contests'

contests_urlpatterns = (
    [
        url(r'^$', views.index, name='list'),
        url(r'^(?P<slug>[-\w]+)/$', views.read, name='read'),
        url(r'^(?P<slug>[-\w+]+)/(?P<participant_id>\d+)/$', views.participant, name='participant_read'),
        url(r'^(?P<slug>[-\w+]+)/add', views.participant_create, name='participant_create'),
    ], 'contests'
)

urlpatterns = [
    url(r'^', include(contests_urlpatterns)),
]
