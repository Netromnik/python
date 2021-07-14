# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.db.models.query import QuerySet


class MagazineQuerySet(QuerySet):
    """Useful QuerySet for magazines"""

    def visible(self):
        """Возвращает видимые журналы"""

        return self.filter(visible=True)
