# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import datetime

from django.db import models
from django.conf import settings

from irk.game.managers import PrizeManager, ProgressManager, PurchaseManager


class Gamer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def __unicode__(self):
        return self.user.profile.full_name


class Prize(models.Model):
    name = models.CharField('Название', max_length=100)
    amount = models.PositiveSmallIntegerField('Количество')
    visible = models.BooleanField('Показывать', default=False)
    price = models.PositiveSmallIntegerField('Цена')
    image = models.ImageField(upload_to='img/site/game/prize', verbose_name=u'Изображение приза')
    slug = models.CharField('Код', max_length=100, default='')

    objects = PrizeManager

    class Meta:
        verbose_name = 'Приз'
        verbose_name_plural = 'Призы'

    def __unicode__(self):
        return self.name


class Treasure(models.Model):
    name = models.CharField('Название', max_length=100)
    secret = models.CharField('Код', max_length=100)
    emoji = models.CharField('Emoji', max_length=10, default='', blank=True)
    svg_emoji = models.CharField('SVG emoji', max_length=255, default='')
    hint = models.CharField('Подсказка', max_length=1000, default='', blank=True)
    visible = models.BooleanField('Показывать', default=False)
    url = models.CharField('Ссылка', max_length=255, default='', blank=True)
    position = models.PositiveIntegerField('Порядок', default=50)

    class Meta:
        verbose_name = 'Клад'
        verbose_name_plural = 'Клады'

    def __unicode__(self):
        return self.name


class Purchase(models.Model):
    gamer = models.ForeignKey(Gamer, verbose_name='Игрок')
    prize = models.ForeignKey(Prize, verbose_name='Приз')
    code = models.CharField('Код для получения приза', default='', blank=True, max_length=20)
    created = models.DateTimeField('Время покупки', default=datetime.datetime.now, blank=True)

    objects = PurchaseManager

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'


class Progress(models.Model):
    gamer = models.ForeignKey(Gamer, verbose_name='Игрок')
    treasure = models.ForeignKey(Treasure, verbose_name='Клад')
    created = models.DateTimeField('Нашел клад', default=datetime.datetime.now, blank=True)

    objects = ProgressManager

    class Meta:
        verbose_name = 'Прогресс'
        verbose_name_plural = 'Прогресс'
