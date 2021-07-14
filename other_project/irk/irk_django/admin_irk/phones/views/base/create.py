# -*- coding: utf-8 -*-

"""Class-based view для создания новой фирмы"""

__all__ = ('CreateFirmBaseView',)

from irk.phones.views.base.mixins import FirmBaseViewMixin


class CreateFirmBaseView(FirmBaseViewMixin):
    """Class-based view для создания новой фирмы"""

    def get(self, request, *args, **kwargs):
        return super(CreateFirmBaseView, self).get(request, self.get_model(request)())

    def post(self, request, *args, **kwargs):
        return super(CreateFirmBaseView, self).post(request, self.get_model(request)())
