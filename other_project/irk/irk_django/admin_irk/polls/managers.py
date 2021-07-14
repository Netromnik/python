# -*- coding: utf-8 -*-

from django.db import models


class PollChoiceManager(models.Manager):

    def get_queryset(self):
        return super(PollChoiceManager, self).get_queryset().order_by('position')
