# -*- coding: utf-8 -*-
# Различные полезные примиси для class based views

from django.db.models import QuerySet

from irk.utils.http import ajax_request


class AjaxMixin(object):
    """Примись облегчающая работу с ajax для class based view"""

    @classmethod
    def as_view(cls, **kwargs):
        view = super(AjaxMixin, cls).as_view(**kwargs)
        return ajax_request(view)


class PaginateMixin(object):
    """Примесь, добавляющая пагинацию"""

    # Индекс элемента с которого начинается выборка
    start_index = 0
    # Количество объектов на странице по умолчанию
    page_limit_default = 20
    # Количество объектов на странице
    page_limit = page_limit_default
    # Максимальное количество объектов на странице
    page_limit_max = page_limit_default

    def _paginate(self, object_list, start_index=None, page_limit=None):
        """
        Разбить набор данных на страницы.

        :param object_list: набор данных
        :return: список объектов на странице и информация о странице
        :rtype: tuple
        """

        if not start_index:
            start_index = self.start_index

        if not page_limit:
            page_limit = self.page_limit

        object_count = object_list.count() if isinstance(object_list, QuerySet) else len(object_list)

        end_index = start_index + page_limit
        end_index = min(end_index, object_count)
        result_list = object_list[start_index:end_index]

        page_info = {
            'has_next': object_count > end_index,
            'next_start_index': end_index,
            'next_limit': min(page_limit, object_count - end_index)
        }

        return result_list, page_info
