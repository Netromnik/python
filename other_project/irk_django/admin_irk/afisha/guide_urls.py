# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.afisha.views import guide

app_name = 'guide'

urlpatterns = [
    # Страница просмотра заведения
    url(r'^(?P<firm_id>\d+)/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', guide.read, name='read'),
    url(r'^(?P<firm_id>\d+)/$', guide.read, name='read'),

    # ajax EndPoints
    url(r'^sessions/(?P<firm_id>\d+)/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$',
        guide.sessions, name='sessions'),
    url(r'^sessions/(?P<firm_id>\d+)/$', guide.sessions, name='sessions'),
    url(r'^calendar/(?P<firm_id>\d+)/$', guide.calendar_paginator, name='calendar_paginator'),

    # Индексная страница
    url(r'^(?P<rub>[^\/]+)/', guide.rubric, name='rubric'),
    url(r'^$', guide.rubric, name='rubric'),
]
