# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.db import models


class BusinessAccount(models.Model):
    """Бизнес аккаунт"""

    name = models.CharField('Название', max_length=250)
    clients = models.ManyToManyField('adv.Client', related_name='clients', verbose_name='Компании')

    class Meta:
        verbose_name = 'Бизнес аккаунт'
        verbose_name_plural = 'Бизнес аккаунты'

    def __unicode__(self):
        return self.name
