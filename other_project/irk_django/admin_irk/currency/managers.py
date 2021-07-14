# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.db.models import Avg, Max, Min


class CurrencyCbrfManager(models.Manager):
    def stat_rates(self, stamp=None):
        if not stamp:
            stamp = self.get_queryset().filter(visible=True).order_by('-stamp').values_list('stamp', flat=True)[0]
        stamp2 = stamp - datetime.timedelta(days=1)

        aggregations = []
        for field in ('usd', 'euro', 'cny'):
            aggregations.append(Min(field))
            aggregations.append(Max(field))
            aggregations.append(Avg(field))

        return super(CurrencyCbrfManager, self).get_queryset().filter(stamp__in=(stamp, stamp2)). \
            order_by('-stamp').aggregate(*aggregations)
