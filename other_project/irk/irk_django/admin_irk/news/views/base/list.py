# -*- coding: utf-8 -*-

"""Class-based view для списка новостей"""

__all__ = ('NewsListBaseView',)

from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View

from irk.news.models import News
from irk.news.permissions import is_site_news_moderator
from irk.news.views.base import SectionNewsBaseView
from irk.utils.helpers import int_or_none


class NewsListBaseView(View):
    """Список новостей раздела"""

    # Модель для вывода объектов
    model = News

    # Шаблон
    template = None

    # Ajax шаблон
    ajax_template = None

    # Порядок сортировки объектов
    ordering = ('-stamp', '-pk')

    # Настройки пагинатора

    # Если указано `False`, метод `get_queryset' должен самостоятельно вернуть список для вывода
    # и осуществлять пагинацию. Используется, например, в raw SQL запросах
    use_pagination = True

    # Класс пагинатора (должен иметь интерфейс `django.core.paginator.Paginator')
    paginator_class = Paginator

    # Количество объектов на странице
    pagination_limit = 20

    by_site = True  # Учитывать в выборке site

    def get(self, request, **kwargs):
        """Обработчик GET запроса"""

        context = self._make_context()

        context.update({
            'objects': context['page_obj'] or context['object_list'],
            'page': self.page,
        })

        return self.render_template(request, context)

    def _make_context(self):
        """Подготовка контекста ответа"""

        self.page = int_or_none(self.request.GET.get('page')) or 1
        self.limit = int_or_none(self.request.GET.get('limit')) or self.pagination_limit

        queryset = self.get_queryset(self.request, self.kwargs)

        if self.use_pagination:
            paginator = self.paginator_class(queryset, self.limit)
            try:
                page_obj = paginator.page(self.page)
                object_list = [obj.cast() for obj in page_obj.object_list]
                page_obj.object_list = object_list
            except (EmptyPage, InvalidPage):
                raise Http404()

            context = {
                'page_obj': page_obj,
                'object_list': object_list,
            }
        else:
            context = {
                'page_obj': None,
                'object_list': queryset,
            }

        context.update(self.extra_context(self.request, queryset, self.kwargs))
        return context

    def get_queryset(self, request, extra_params=None):
        """Получаем queryset новостей для списка

        Параметры::
            request: объект класса `django.http.HttpRequest'
            extra_params: словарь всех параметров, получаемых view
        """

        queryset = self.model.material_objects
        if self.by_site:
            queryset = queryset.for_site(request.csite.site, search_source_site=True)
        queryset = queryset.order_by(*self.ordering).distinct()

        if not self.show_hidden(request):
            queryset = queryset.filter(is_hidden=False)
        return queryset

    def show_hidden(self, request):
        """Хелпер, определяющий, показывать ли скрытые новости

        Используется, например, если пользователь является модератором
        """

        return is_site_news_moderator(request)

    def extra_context(self, request, queryset, extra_params=None):
        """Дополнительные данные для передачи в шаблон

        Параметры::
            request: объект класса `django.http.HttpRequest'
            queryset: QuerySet объектов, возвращаемый ``get_queryset``
            extra_params: словарь всех параметров, получаемых view
        """

        if extra_params:
            return extra_params.get('context', {})
        return {}

    def get_template(self, request, template_context):
        """Выбор шаблона для рендеринга

        Может возвращать список шаблонов, из которых будет выбран первый существующий

        Параметры::
            request: объект класса `django.http.HttpRequest'
            template_context: словарь данных, который будет передан в шаблон
        """

        if self.template:
            return self.template

        opts = self.model._meta
        object_name = opts.object_name.lower()

        if 'special' in self.__module__:
            return 'special/%s/index.html' % object_name

        return '%s/%s/index.html' % (opts.app_label, object_name)

    def get_ajax_template(self, request, template_context):
        """Выбор шаблона для рендеринга ajax

        Может возвращать список шаблонов, из которых будет выбран первый существующий

        Параметры::
            request: объект класса `django.http.HttpRequest'
            template_context: словарь данных, который будет передан в шаблон
        """

        return self.ajax_template

    def render_template(self, request, context):
        """Рендеринг шаблона

        Параметры::
            request: объект класса `django.http.HttpRequest'
            context: словарь данных, который будет передан в шаблон
        """
        if request.is_ajax():
            template = self.get_ajax_template(request, context)
            if template:
                return render(request, template, context)

            return HttpResponseBadRequest('AJAX is not supported')

        return render(request, self.get_template(request, context), context)


class NewsCategoryBaseView(SectionNewsBaseView, NewsListBaseView):
    """Список новостей отдельной категории

    Из URL должен передаваться slug категории новостей, например::

        ^/news/(?P<slug>\w+)/$

    """

    def get_queryset(self, request, extra_params=None):
        try:
            self.category = get_object_or_404(self.category_model, slug=extra_params['slug'])
        except KeyError:
            raise Http404()

        queryset = super(NewsCategoryBaseView, self).get_queryset(request, extra_params).filter(sites=request.csite.site)

        if self.category_model is not None:
            queryset = queryset.filter(**{
                self.category_model_field: self.category,
            })

        return queryset

    def extra_context(self, request, queryset, extra_params=None):
        context = super(NewsCategoryBaseView, self).extra_context(request, queryset, extra_params)
        context['category'] = self.category

        return context
