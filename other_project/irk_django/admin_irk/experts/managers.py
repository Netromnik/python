# -*- coding: utf-8 -*-

from django.db import models


class ExpertManager(models.Manager):
    def conferences(self):
        """Конференции"""

        return self.get_queryset().filter(is_consultation=False)

    def consultations(self):
        """Консультации"""

        return self.get_queryset().filter(is_consultation=True)
