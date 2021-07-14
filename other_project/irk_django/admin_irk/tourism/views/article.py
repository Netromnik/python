# -*- coding: utf-8 -*-

from __future__ import absolute_import

from irk.news.views.articles import ArticleReadView
from irk.tourism.models import Article


class ReadView(ArticleReadView):
    model = Article
    template = 'tourism/blog/read.html'


read = ReadView.as_view()
