# -*- coding: utf-8 -*-

"""Class-based view для списка фирм"""

__all__ = ('ListFirmBaseView',)

from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import render
from django.views.generic.base import View

from irk.phones.models import Firms


class ListFirmBaseView(View):
    """Список фирм"""

    model = Firms
    template = None

    def get(self, request, **kwargs):
        if not self.template:
            raise ImproperlyConfigured(u'Не указан шаблон для вывода данных')

        try:
            page = int(request.GET.get('page'))
        except (TypeError, ValueError):
            page = 1

        try:
            limit = int(request.GET.get('limit'))
        except (TypeError, ValueError):
            limit = 20

        queryset = self.get_queryset(request, kwargs)

        paginate = Paginator(queryset, limit)
        try:
            objects = paginate.page(page)
        except (EmptyPage, InvalidPage):
            objects = paginate.page(1)

        self.page = page

        context = {
            'objects': objects,
            'page': page,
        }
        context.update(self.extra_context(request, queryset, kwargs))

        return render(request, self.template, context)

    def get_queryset(self, request, extra_params=None):
        """Получаем queryset фирм для списка

        Параметры::
            request: объект класса `django.http.HttpRequest'
            extra_params: словарь всех параметров, получаемых view
        """

        queryset = self.model.objects.filter(is_active=True)
        if not self.show_hidden(request):
            queryset = queryset.filter(visible=True)

        return queryset

    def show_hidden(self, request):
        """Хелпер, определяющий, показывать ли скрытые фирмы

        Используется, например, если пользователь является модератором
        """

        return False

    def extra_context(self, request, queryset, extra_params=None):
        """Дополнительные данные для передачи в шаблон

        Параметры::
            request: объект класса `django.http.HttpRequest'
            queryset: QuerySet объектов, возвращаемый ``get_queryset``
            extra_params: словарь всех параметров, получаемых view
        """

        return {}
