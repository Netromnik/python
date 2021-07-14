# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from irk.news.models import Podcast
from irk.news.views import NewsReadBaseView
from irk.news.views.base.list import NewsListBaseView


class PodcastListView(NewsListBaseView):
    model = Podcast
    template = 'news-less/podcast/index.html'
    ajax_template = 'news-less/podcast/snippets/entries.html'
    pagination_limit = 7


index = PodcastListView.as_view()


class PodcastReadView(NewsReadBaseView):
    template = 'news-less/podcast/read.html'
    model = Podcast


read = PodcastReadView.as_view()
