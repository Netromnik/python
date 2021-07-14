# -*- coding: utf-8 -*-
"""Gallery checks for System check framework (Django 1.7)"""

from django.contrib.contenttypes.admin import GenericInlineModelAdminChecks


class GalleryInlineModelAdminChecks(GenericInlineModelAdminChecks):
    """Проверки для Галереи в админке"""

    def _check_relation(self, cls, parent_model):
        # Отменяет проверку наличия ForeignKey cls.model на parent_model т.к.
        # вместо cls.model подставляется объект Gallery

        return []
