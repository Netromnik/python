# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.polls import views

app_name = 'polls'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<year>\d+)/$', views.year, name='year'),
    url(r'^vote/$', views.vote, name='vote'),
    url(r'^delete_vote/$', views.delete_vote, name='delete_vote'),
    url(r'^vote_quiz/$', views.vote_quiz, name='vote_quiz'),
    url(r'^(?P<year>\d{4})/(?P<poll_id>\d+)/', views.results, name='results'),
]
