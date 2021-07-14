# -*- coding: UTF-8 -*-

"""
У нас есть старые новости/статьи из закрытых разделов, на которые сделаны редиректы в nginx.
При этом новости/статьи остались привязаны к старому разделу в базе. Например, при поиске по новостям в результат
попадает одна из таких статей/новостей, и при выводе результатов поиска шаблон попытется сделать reverse
по уже несуществуюшему конфигу урлов, что вызовет 404 на всю страницу результата поиска. Данная заглушка позволяет
корректно отрабатывать реверсу.
"""

from django.conf.urls import url
from django.http import HttpResponse


empty = lambda *args, **kwargs: HttpResponse()

urlpatterns = [

    # 2013
    url(r'^2013/articles/$', empty, name='newyear.views.articles.list'),
    url(r'^2013/articles/(?P<article_id>\d+)/$', empty, name='newyear.views.articles.read'),
    url(r'^2013/news/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', empty,
        name='newyear.news.read'),
    url(r'^2013/news/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', empty, name='newyear.news.date'),
    url(r'^2013/news/$', empty, name='newyear.news.index'),

    # Работа
    url(r'^job/articles/$', empty, name='jobs.views.articles.list'),
    url(r'^job/article/$', empty, name='jobs.views.articles.list'),
    url(r'^job/articles/(?P<article_id>\d+)/$', empty, name='jobs.views.articles.read'),
    url(r'^job/news/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', empty,
        name='jobs.news.read'),
    url(r'^job/news/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', empty, name='jobs.news.date'),
    url(r'^job/news/$', empty, name='jobs.news.index'),

    # svadba
    url(r'^svadba/article/$', empty, name='shopping.news.index'),
    url(r'^svadba/article/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', empty, name='shopping.news.date'),
    url(r'^svadba/article/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', empty,
        name='shopping.news.read'),

    # sochi2014
    url(r'^sochi2014/news/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', empty,
        name='sochi2014.news.read'),

    # bandy2014
    url(r'^bandy2014/news/', empty, name='bandy2014.news.index'),
    url(r'^bandy2014/news/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', empty, name='bandy2014.news.date'),
    url(r'^bandy2014/news/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', empty,
        name='bandy2014.news.read'),
    url(r'^bandy2014/article/$', empty, name='bandy2014.article.index'),
    url(r'^bandy2014/article/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', empty, name='bandy2014.article.date'),
    url(r'^bandy2014/article/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', empty,
        name='bandy2014.article.read'),
    url(r'^bandy2014/photo/$', empty, name='bandy2014.photo.index'),
    url(r'^bandy2014/photo/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', empty, name='bandy2014.photo.date'),
    url(r'^bandy2014/photo/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', empty,
        name='bandy2014.photo.read'),
    url(r'^bandy2014/video/$', empty, name='bandy2014.video.index'),
    url(r'^bandy2014/video/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', empty, name='bandy2014.video.date'),
    url(r'^bandy2014/video/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', empty,
        name='bandy2014.video.read'),
]
