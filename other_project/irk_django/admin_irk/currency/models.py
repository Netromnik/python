# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models

from irk.currency.managers import CurrencyCbrfManager
from irk.phones.models import Firms as Firm, SectionFirm
from irk.utils.db.models import Loggable


class CurrencyCbrf(Loggable, models.Model):
    """Курс ЦБ РФ"""

    stamp = models.DateField(primary_key=True)
    usd = models.FloatField(u'Курс доллара США', blank=True)
    euro = models.FloatField(u'Курс евро', db_column='euro', blank=True)
    cny = models.FloatField(u'Курс юаня', blank=True)
    visible = models.BooleanField(u'Отображать', db_index=True, default=False)  # TODO Больше не используется

    objects = CurrencyCbrfManager()

    class Meta:
        db_table = u'currency_base'
        verbose_name = u'курс ЦБ РФ'
        verbose_name_plural = u'курсы ЦБ РФ'


class ExchangeRate(models.Model):
    """Курс обмена валюты"""

    numeral_code = models.PositiveIntegerField(u'Числовой код')
    code = models.CharField(u'Код валюты', max_length=5, unique=True)
    name = models.CharField(u'Название', max_length=255)
    nominal = models.PositiveIntegerField(u'Номинал')
    value = models.FloatField(u'Значение')

    class Meta:
        db_table = 'currency_exchange_rates'
        verbose_name = u'курс обмена'
        verbose_name_plural = u'курсы обмена'
