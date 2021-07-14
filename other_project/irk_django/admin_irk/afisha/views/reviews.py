# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.core.urlresolvers import reverse

from irk.afisha.models import Review
from irk.news.views.base.list import NewsListBaseView
from irk.news.views.base.read import SectionNewsReadBaseView


class ReviewListView(NewsListBaseView):
    model = Review

    def get_queryset(self, request, extra_params=None):
        # хак: приходится вручную обращаться к полям `article_ptr`, чтобы django сделало left join таблицы статей
        # так как в выборке используется поиск по полю `news.models.BaseMaterial.serialized_sites`
        qs = super(ReviewListView, self).get_queryset(request, extra_params)
        qs = qs.filter(article_ptr__id__isnull=False, article_ptr__comments_cnt__gte=0)
        return qs


index = ReviewListView.as_view()


class ReviewReadView(SectionNewsReadBaseView):
    model = Review

read = ReviewReadView.as_view()
