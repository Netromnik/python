# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from irk.news.models import Video
from irk.news.views.base.list import NewsListBaseView
from irk.news.views.base.read import NewsReadBaseView


class VideoListView(NewsListBaseView):
    model = Video
    template = 'news-less/video/index.html'
    ajax_template = 'news-less/video/snippets/entries.html'
    pagination_limit = 7


index = VideoListView.as_view()


class VideoReadView(NewsReadBaseView):
    template = 'news-less/video/read.html'
    model = Video


read = VideoReadView.as_view()
