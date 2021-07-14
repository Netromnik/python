# -*- coding: utf-8 -*-

from django.core.paginator import Paginator, Page


class ReversePaginator(Paginator):
    """
    Разбивает списки не по [10, 10, 3], где 3 - последняя страница,
    а [3, 10, 10], где 3 - первая страница
    """

    def page(self, number):
        number = self.validate_number(number)
        rest = abs(self.count - self.num_pages * self.per_page)
        top = (number - 1) * self.per_page + self.per_page
        if top > self.count:
            top = self.count
        else:
            top -= rest
        bottom = top - self.per_page
        if bottom < 1:
            bottom = 0
        return Page((self.object_list[bottom:top])[::-1], number, self)
