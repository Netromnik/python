# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from irk.news.models import BaseMaterial, Metamaterial
from irk.news.views.base.list import NewsListBaseView
from irk.news.views.base.read import SectionNewsReadBaseView
from irk.obed.models import Article, Review, ArticleCategory, Poll, Test, TildaArticle
from irk.obed.permissions import can_edit_news, is_moderator
from irk.utils.helpers import int_or_none
from irk.utils.http import JsonResponse


class ArticleListView(NewsListBaseView):
    model = Article
    template = 'obed/article/index.html'
    ajax_template = 'obed/article/article_list.html'

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.ajax_get(request, *args, **kwargs)

        return super(ArticleListView, self).dispatch(request, *args, **kwargs)

    def ajax_get(self, request, *args, **kwargs):
        context = self._make_context()
        return render(request, self.ajax_template, context)

    def get_queryset(self, request, extra_params=None):
        queryset = self._get_base_queryset()

        # Исключение объекта из списка
        exclude_id = int_or_none(self.request.GET.get('exclude_id'))
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)

        if not is_moderator(self.request.user):
            queryset = queryset.filter(is_hidden=False)

        return queryset.select_subclasses()

    def _get_base_queryset(self):
        """Базовый QuerySet"""

        material_types = [Article, Review, Poll, Metamaterial, Test, TildaArticle]

        queryset = BaseMaterial.material_objects \
            .filter_models(*material_types) \
            .filter(sites=self.request.csite) \
            .order_by('-stamp', '-published_time') \
            .select_related('source_site') \
            .select_subclasses(*material_types)

        return queryset


class CategoryArticleListView(ArticleListView):
    def _get_base_queryset(self):
        section_category = get_object_or_404(ArticleCategory, slug=self.kwargs.get('section_category_slug'))
        queryset = self.model.objects.filter(section_category=section_category).order_by('-stamp', '-published_time')

        return queryset


class SeeAlsoListArticleView(ArticleListView):
    ajax_template = 'obed/article/see_also_list.html'

    def get_queryset(self, request, extra_params=None):
        category_id = self.kwargs.get('category_id')
        article_category = get_object_or_404(ArticleCategory, pk=category_id)

        queryset = Article.material_objects.filter(section_category=article_category).order_by('-stamp',
                                                                                               '-published_time')
        if not can_edit_news(self.request.user):
            queryset = queryset.filter(is_hidden=False)

        return queryset

    def ajax_get(self, request, *args, **kwargs):
        context = self._make_context()

        return JsonResponse(dict(
            html=render_to_string(self.ajax_template, {'object_list': context['object_list']}, request=request),
            has_next=context['has_next'],
            next_start_index=context['next_start_index'],
            next_limit=context['next_limit'],
        ))

    def _make_context(self):
        if self.request.is_ajax():
            self.start_index = int_or_none(self.request.GET.get('start')) or 0
            self.limit = int_or_none(self.request.GET.get('limit')) or self.pagination_limit

            queryset = self.get_queryset(self.request, self.kwargs)
            object_count = queryset.count()

            end_index = self.start_index + self.limit
            end_index = min(end_index, object_count)
            object_list = queryset[self.start_index:end_index]
            context = {
                'object_list': object_list,
                'has_next': object_count > end_index,
                'next_start_index': end_index,
                'next_limit': min(self.limit, object_count - end_index)
            }
        else:
            context = super(SeeAlsoListArticleView, self)._make_context()
        return context


class ArticleReadView(SectionNewsReadBaseView):
    model = Article

    def extra_context(self, request, obj, extra_params=None):
        context = super(ArticleReadView, self).extra_context(request, obj, extra_params=extra_params)

        articles = Article.objects.filter(section_category=obj.section_category).exclude(pk=obj.pk) \
            .order_by('-stamp', '-published_time').select_subclasses('obed_review')
        if not can_edit_news(request.user):
            articles = articles.filter(is_hidden=False)

        limit = 5
        context['see_also'] = articles[:limit]
        context['has_next'] = articles.count() > limit

        return context


class ReviewReadView(ArticleReadView):
    model = Review
    template = 'obed/review/read.html'


class TildaReadView(SectionNewsReadBaseView):
    model = TildaArticle
    template = 'obed/tilda/read.html'


article_list = ArticleListView.as_view()
article_read = ArticleReadView.as_view()
category_article_list = CategoryArticleListView.as_view()
review_read = ReviewReadView.as_view()
see_also_list = SeeAlsoListArticleView.as_view()
tilda_read = TildaReadView.as_view()
