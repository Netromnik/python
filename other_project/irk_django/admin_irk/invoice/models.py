from __future__ import absolute_import, unicode_literals

from uuid import uuid4

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


def get_uuid():
    return str(uuid4()).replace('-', '').upper()[:10]


class Invoice(models.Model):
    class COMPANY:
        MONETA = 'moneta'
        APPLE = 'apple'

        CHOICES = (
            (MONETA, 'Монета.ру'),
            (APPLE, ' App Store'),
        )

    class STATUS:
        PROCESSED = 'processed'
        HOLD = 'hold'
        CANCEL = 'cancel'
        SUCCESS = 'success'
        FAIL = 'fail'

        CHOICES = (
            (PROCESSED, 'Ожидание оплаты'),
            (CANCEL, 'Отменен'),
            (SUCCESS, 'Успешно'),
            (FAIL, 'Ошибка'),
        )

    class CURRENCY:
        RUB = 'RUB'
        USD = 'USD'
        EUR = 'EUR'

        CHOICES = (
            (RUB, 'Рубли'),
            (USD, 'Доллары США'),
            (EUR, 'Евро'),
        )

    number = models.CharField('Номер заказа', unique=True, max_length=64, default=get_uuid)
    status = models.CharField('Результат', max_length=16, choices=STATUS.CHOICES, default=STATUS.PROCESSED)
    system = models.PositiveIntegerField('Способ платежа', blank=True, null=True)
    invoice = models.CharField('Номер операции оператора', max_length=64, blank=True, null=True)
    amount = models.FloatField('Сумма заказа')
    currency = models.CharField('Валюта', blank=True, null=True, max_length=3, default=CURRENCY.RUB,
                                choices=CURRENCY.CHOICES)
    created = models.DateTimeField('Создан', auto_now_add=True)
    performed_datetime = models.DateTimeField('Обработан', blank=True, null=True)

    company = models.CharField('Платежная компания', max_length=16, choices=COMPANY.CHOICES, default=COMPANY.MONETA)

    __original_status = None

    class Meta:
        ordering = ('-created',)
        verbose_name = 'платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return self.number

    @property
    def is_payed(self):
        return self.status == self.STATUS.SUCCESS


class BaseOrder(models.Model):
    """Базовый класс для всех заказов"""

    user = models.ForeignKey(User, verbose_name=u'Пользователь', null=True, default=None, on_delete=models.CASCADE)
    price = models.FloatField(u'Сумма заказа')
    invoice = models.OneToOneField(Invoice, verbose_name=u'Платеж', related_name='order_invoice', null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(u'Дата добавления', auto_now_add=True)
    updated = models.DateTimeField(u'Дата последнего обновления', auto_now=True)
    content_type = models.ForeignKey(ContentType, editable=False, null=True, blank=True, on_delete=models.CASCADE)
    content_object = GenericForeignKey('content_type', 'id')


    def __str__(self):
        return u'{}'.format(self.pk)

    class Meta:
        verbose_name = u'Заказ'
        verbose_name_plural = u'Заказы'

    def save(self, *args, **kwargs):

        if not self.pk:
            self.content_type = ContentType.objects.get_for_model(self, for_concrete_model=False)

        super(BaseOrder, self).save(*args, **kwargs)
