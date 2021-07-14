# -*- coding: utf-8 -*-

"""Class-based view для просмотра одной фирмы"""

__all__ = ('ReadFirmBaseView',)

from django.http import HttpResponse, Http404
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View

from irk.phones.models import Firms as Firm


class ReadFirmBaseView(View):
    model = Firm
    template = None
    redirect_url = None

    def get(self, request, **kwargs):
        """Обработка GET запроса"""

        obj = self.get_object(request, kwargs)
        if isinstance(obj, HttpResponse):
            return obj

        context = {
            'object': obj,
        }
        context.update(self.extra_context(request, obj, kwargs))

        return render(request, self.get_template(request, obj, context), context)

    def get_object(self, request, extra_params=None):
        """Хелпер. возвращающий объект класса ``self.model``

        Параметры::
            request: объект класса `django.http.HttpRequest'
            extra_params: словарь параметров, переданных в view

        Если возвращается `django.http.HttpResponse' или его потомок, этот объект сразу отдается клиенту.
        Это позволит делать дополнительные проверки, можно ли редактировать пользователю этот объект.
        """

        obj = self.model.objects.filter(pk=extra_params['firm_id'], visible=True).first()

        # Переадресация на индекс раздела если объект не найден
        if not obj:
            if self.redirect_url:
                return redirect(self.redirect_url, permanent=True)
            raise Http404()
        return obj

    def extra_context(self, request, obj, extra_params=None):
        """Дополнительные данные для передачи в шаблон

        Параметры::
            request: объект класса `django.http.HttpRequest'
            obj: объект класса ``self.model``
            extra_params: словарь параметров, переданных в view

        Должен возвращаться словарь
        """

        return {}

    def get_template(self, request, obj, template_context):
        """Выбор шаблона для рендеринга

        Может возвращать список шаблонов, из которых будет выбран первый существующий

        Параметры::
            request: объект класса `django.http.HttpRequest'
            obj: объект класса ``self.model``
            template_context: словарь данных, который будет передан в шаблон
        """

        if not self.template:
            raise ImproperlyConfigured(u'Не указан шаблон для вывода данных')

        return self.template
