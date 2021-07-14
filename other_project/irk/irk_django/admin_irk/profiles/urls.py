# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from irk.profiles import views
from irk.profiles.views import bookmarks, users

app_name = 'profiles'

bookmark_urlpatterns = (
    [
        url(r'^$', bookmarks.index, name='index'),
        url(r'^add/$', bookmarks.add, name='add'),
        url(r'^remove/$', bookmarks.remove, name='remove'),
    ], 'bookmark'
)

urlpatterns = [
    url(r'^set_option/$', views.set_option, name='set_option'),
    url(r'^(?P<user_id>\d+)/ban/$', views.ban, name='ban'),
    url(r'^(?P<pk>\d+)/avatar-remove/$', users.avatar_remove, name='avatar_remove'),
    url(r'^(?P<user_id>\d+)-(.*?)/$', users.read, name='read'),
    url(r'^(?P<profile_id>\d+)/close/$', views.close, name='close'),
    url(r'^bookmark/', include(bookmark_urlpatterns)),
]
