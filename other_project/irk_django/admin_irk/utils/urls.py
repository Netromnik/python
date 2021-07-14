# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.utils import views
from irk.utils.views import admin

app_name = 'utils'

urlpatterns = [
    url(r'objects/(?P<id>\d+)/$', views.get_objects, name='get_objects'),
    url(r'sections/$', views.sections_suggest, name='sections_suggest'),
    url(r'streets/$', views.streets_suggest, name='streets_suggest'),
    url(r'report/$', views.report, name='report'),
    url(r'^navigation/$', views.navigation_bar, name='navigation_bar'),
    url(r'^admin/edit-notifications/$', admin.edit_notification, name='edit_notification'),
]
