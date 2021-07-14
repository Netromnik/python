# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.db import models

from irk.comments.helpers import content_type_for_comments


class PrizeQuerySet(models.QuerySet):

    def visible(self):
        return self.filter(visible=True)

PrizeManager = PrizeQuerySet.as_manager()


class ProgressQuerySet(models.QuerySet):

    def for_gamer(self, gamer_id):
        return self.filter(gamer_id=gamer_id)

ProgressManager = ProgressQuerySet.as_manager()


class PurchaseQuerySet(models.QuerySet):

    def for_gamer(self, gamer_id):
        return self.filter(gamer_id=gamer_id)

PurchaseManager = PurchaseQuerySet.as_manager()
