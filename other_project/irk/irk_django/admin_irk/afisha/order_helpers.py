# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import urllib

from django.conf import settings

from irk.afisha.models import EventOrder
from irk.invoice.order_helpers import BaseOrderHelper
from irk.invoice.models import Invoice
from irk.utils.notifications import tpl_notify


class EventOrderHelper(BaseOrderHelper):
    """Управление заказами на размещение событий"""

    order_class = EventOrder

    def __init__(self, event, request=None):
        self.event = event
        self.request = request

    def get_order(self):
        return EventOrder.objects.filter(event_id=self.event.pk).order_by('-pk').first()

    def create_invoice(self):
        """Создание платежа"""
        order = self.get_order()

        invoice = Invoice(amount=order.price)
        invoice.save()

        order.invoice = invoice
        order.save()

        self.send_invoice()

        return invoice

    def send_invoice(self):
        """Отправить ссылку на оплату по почте"""

        order = self.get_order()

        context = {
            'url': self.get_invoice_url(),
            'event': order.event,
        }

        tpl_notify('Оплата размещения в афише Irk.ru', 'afisha/notif/invoice.html', context,
                   emails=[self.event.organizer_email, ])

    def get_mnt_description(self):
        return 'Оплата размещения события на сайте Irk.ru'.encode('utf8')

    @staticmethod
    def invoice_success_status(invoice):
        """Резместить событие при оплате"""
        order = invoice.order_invoice.content_object
        event = order.event
        event.is_hidden = False
        event.save()
