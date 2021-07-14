# -*- coding: utf-8 -*-

from __future__ import absolute_import

from irk.news.models import News
from irk.news.views.base.list import NewsListBaseView
from irk.news.views.base.read import NewsReadBaseView


class NewsListView(NewsListBaseView):
    model = News
    template = 'afisha/news/list.html'

list = NewsListView.as_view()


class NewsReadView(NewsReadBaseView):
    model = News

read = NewsReadView.as_view()
