# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from django.conf.urls import url

from irk.magazine import views

app_name = 'magazine'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # Подписка на журнал
    url(r'^subscription_ajax/$', views.subscription_ajax, name='subscribe'),
    url(r'^subscription_unsubscribe/$', views.subscription_unsubscribe, name='unsubscribe'),
    url(r'^subscription_confirm/$', views.subscription_confirm, name='confirm'),

    url(r'^(?P<magazine_slug>[\w-]+)/(?P<material_id>\d+)/$', views.material_router, name='router'),
    url(r'^(?P<slug>[\w-]+)/$', views.read, name='read'),
]
