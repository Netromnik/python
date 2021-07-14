# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.db.models import Q
from django.views.generic.base import View

from irk.news import settings as app_settings
from irk.news.controllers import ArticleIndexController
from irk.news.models import Article, Category, TildaArticle
from irk.news.views.base.date import NewsDateBaseView
from irk.news.views.base.list import NewsCategoryBaseView
from irk.news.views.base.read import NewsReadBaseView
from irk.utils.helpers import int_or_none
from irk.utils.http import JsonResponse


class ArticleIndexView(View):

    template_name = 'news-less/article/index.html'
    ajax_template = 'news-less/article/snippets/entries.html'
    pagination_limit = 20

    def get(self, request):
        context = self.get_context_data()

        if request.is_ajax():
            return JsonResponse({
                'html': render_to_string(self.ajax_template, context, request=request),
                'has_next': context['has_next'],
                'next_limit': context['next_limit'],
                'next_start_index': context['next_start_index'],
            })

        return render(request, self.template_name, context)

    def get_context_data(self):
        context = {}

        limit = int_or_none(self.request.GET.get('limit')) or self.pagination_limit
        page = int_or_none(self.request.GET.get('page')) or 1
        start = int_or_none(self.request.GET.get('start')) or 0

        controller = ArticleIndexController()
        next_index, groups = controller.layout_groups(page, start, limit)
        context['layout_groups'] = groups
        context['has_next'] = bool(next_index)
        context['next_start_index'] = next_index
        context['next_limit'] = 20

        if page == 1:
            context['supermaterial'] = controller.get_supermaterial()

        return context


index = ArticleIndexView.as_view()


class ArticleCategoryView(NewsCategoryBaseView):
    model = Article
    category_model = Category
    category_model_field = 'category'
    pagination_limit = 10

    def get_template(self, request, template_context):
        category = template_context['category']

        return ('news-less/article/%s/category.html' % category.slug, 'news-less/article/category.html')


category = ArticleCategoryView.as_view()


class ArticleReadView(NewsReadBaseView):
    model = Article

    def get_template(self, request, obj, template_context):
        templates = ['news-less/article/read.html']

        if obj.magazine:
            return 'magazine/article/read.html'

        if obj.project_id:
            special = 'news-less/special/{}/read.html'.format(obj.project.slug)
            templates.insert(0, special)

        return templates


read = ArticleReadView.as_view()
