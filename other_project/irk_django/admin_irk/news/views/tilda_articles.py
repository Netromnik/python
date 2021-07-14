# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from irk.news.models import TildaArticle
from irk.news.views.base.read import NewsReadBaseView


class ArticleReadView(NewsReadBaseView):
    model = TildaArticle

    def get_template(self, request, obj, template_context):
        return 'news-less/tilda/read.html'


read = ArticleReadView.as_view()
