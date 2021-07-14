# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.experts import views

app_name = 'experts'

# Пресс-конференции
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^subscription/$', views.subscription, name='subscription'),
    url(r'^(?P<category_alias>\w+)/(?P<expert_id>\d+)/$', views.read, name='read'),
    url(r'^(?P<category_alias>\w+)/(?P<expert_id>\d+)/reply/$', views.question_reply, name='question_reply'),
    url(r'^(?P<category_alias>\w+)/(?P<expert_id>\d+)/question/$', views.question_create, name='question_create'),
    url(r'^(?P<category_alias>\w+)/(?P<expert_id>\d+)/delete/(?P<question_id>\d+)/$', views.question_delete,
        name='question_delete'),
]
