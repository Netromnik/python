# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from irk.recycle import admin_views, views

app_name = 'recycle'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/categories/$', admin_views.categories, name='admin_categories'),
    url(r'^admin/save_order/$', admin_views.save_order, name='admin_save_order'),
    url(r'^admin/article/$', admin_views.article, name='admin_article'),
    url(r'^admin/change_article_status/$', admin_views.change_article_status, name='admin_change_article_status'),
    url(r'^admin/added_article/$', admin_views.added_article, name='admin_added_article'),
]
