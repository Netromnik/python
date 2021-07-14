# -*- coding: utf-8 -*-

"""Class-based view для редактирования фирмы"""

__all__ = ('UpdateFirmBaseView',)

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from irk.phones.views.base.mixins import FirmBaseViewMixin


class UpdateFirmBaseView(FirmBaseViewMixin):
    """Class-based view для редактирования фирмы"""

    def get_object(self, request, extra_params):
        """Хелпер, возвращающий объект для редактирования

        Если возвращается `django.http.HttpResponse' или его потомок, этот объект сразу отдается клиенту.
        Это позволит делать дополнительные проверки, можно ли редактировать пользователю этот объект.

        Параметры::
            request: объект класса `django.http.HttpRequest'
            extra_params: словарь переданных параметров во view
        """

        return get_object_or_404(self.model, pk=extra_params['firm_id'])

    def get(self, request, **kwargs):
        obj = self.get_object(request, kwargs)
        if isinstance(obj, HttpResponse):
            return obj

        return super(UpdateFirmBaseView, self).get(request, obj)

    def post(self, request, **kwargs):
        obj = self.get_object(request, kwargs)
        if isinstance(obj, HttpResponse):
            return obj

        return super(UpdateFirmBaseView, self).post(request, obj)
