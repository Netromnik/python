# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url, include

from irk.irkutsk360 import views

app_name = 'irkutsk360'


congratulations_urlpatterns = (
    [
    url(r'^$', views.CongratulationsView.as_view(), name='index'),
    url(r'^add/$', views.CongratulationsFormView.as_view(), name='add'),
    ], 'congratulations'
)

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^afisha/$', views.afisha360_index, name='afisha'),
    url(r'^gallery/$', views.GalleryView.as_view(), name='gallery'),
    url(r'^stories/$', views.StoryView.as_view(), name='stories'),
    url(r'^congratulations/', include(congratulations_urlpatterns)),
    url(r'^next-fact/(?P<number>\d+)/$', views.FactView.as_view(), name='next_fact'),
]
