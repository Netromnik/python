# -*- coding: utf-8 -*-

import datetime

from irk.news.models import Photo
from irk.news.views.base.read import NewsReadBaseView
from irk.news.views.base.list import NewsListBaseView
from irk.news.user_options import PhotoFullscreenHintOption


class PhotoReadView(NewsReadBaseView):
    model = Photo
    template = 'news-less/photo/read.html'

    def get_template(self, request, obj, context):
        if obj.magazine:
            return 'magazine/photo/read.html'

        return self.template

    def extra_context(self, request, obj, extra_params=None):
        context = super(PhotoReadView, self).extra_context(request, obj, extra_params)

        # Другие фоторепортажи
        other = self.model.objects.filter(sites=request.csite).exclude(pk=obj.pk).order_by('-stamp')
        if not self.show_hidden(request):
            other = other.filter(is_hidden=False)
        context['other'] = other[:3]

        # Сообщаем о полноэкранном режиме только до 10.04.05
        if datetime.date.today() > datetime.date(2015, 4, 10):
            show_hint = 2
        else:
            show_hint = PhotoFullscreenHintOption(request).value
        context['show_photo_fullscreen_hint'] = show_hint

        return context


read = PhotoReadView.as_view()


class PhotoListView(NewsListBaseView):
    model = Photo
    template = 'news-less/photo/index.html'
    ajax_template = 'news-less/photo/snippets/entries.html'
    pagination_limit = 10

    def get_queryset(self, request, extra_params=None):
        queryset = super(PhotoListView, self).get_queryset(request, extra_params)

        return queryset.select_subclasses()


index = PhotoListView.as_view()
