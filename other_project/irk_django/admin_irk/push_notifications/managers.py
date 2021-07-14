# -*- coding: utf-8 -*-

from django.db.models.query import QuerySet


class DeviceQuerySet(QuerySet):
    """Useful QuerySet for devices"""

    def active(self):
        """Возвращает активныеустройства"""

        return self.filter(is_active=True)


DeviceManager = DeviceQuerySet.as_manager()
