# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Fact(models.Model):

    number = models.IntegerField('Номер')
    content = models.CharField('Содержание', max_length=200)

    class Meta:
        verbose_name = 'Факт'
        verbose_name_plural = 'Факты'
        ordering = ['number']

    def __unicode__(self):
        return str(self.number)


class Congratulation(models.Model):

    name = models.CharField('Имя', max_length=200)
    contact = models.CharField('Контакты', max_length=200)
    position = models.CharField('Должность', max_length=200)
    content = models.CharField('Содержание', max_length=200)
    is_visible = models.BooleanField(u'Показывать', default=False, db_index=True)
    photo = models.ImageField(upload_to='img/site/irkutsk360/congratulation', verbose_name=u'Фото', blank=True,
        help_text=u'60x60')

    class Meta:
        verbose_name = 'Поздравление'
        verbose_name_plural = 'Поздравления'

    def __unicode__(self):
        return self.name
