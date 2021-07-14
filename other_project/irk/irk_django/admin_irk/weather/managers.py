# -*- coding: utf-8 -*-

from django.db.models.query import QuerySet


class WishForConditionsQuerySet(QuerySet):
    """Useful QuerySet for wishes"""

    def active(self):
        """Возвращает активные пожелания"""

        return self.filter(is_active=True)

    def by_month(self, month):
        """Возвращает пожелания на определенный месяц"""

        params = None

        if isinstance(month, int):
            params = {'months__number': month}

        if isinstance(month, basestring):
            params = {'months__alias': month}

        if not params:
            return self

        return self.filter(**params)
