import urllib

from django.conf import settings

from .models import Invoice


class BaseOrderHelper(object):
    """Управление заказами"""

    order_class = None

    def __init__(self, request=None):
        self.request = request

    def create_order(self, data):
        """Создание заказа"""
        order = self.order_class(**data)
        if self.request and self.request.user.is_authenticated:
            order.user = self.request.user
        order.save()
        return order

    def get_order(self):
        raise NotImplementedError

    def create_invoice(self):
        """Создание платежа"""
        order = self.get_order()
        invoice = Invoice(amount=order.price)
        invoice.save()
        return invoice

    def send_invoice(self):
        raise NotImplementedError

    def get_mnt_description(self):
        """Сформировать описание платежа"""
        raise NotImplementedError

    def get_invoice_url(self):

        order = self.get_order()

        params = {
            'MNT_ID': settings.MNT_ID,
            'MNT_TRANSACTION_ID': order.invoice.number,
            'MNT_CURRENCY_CODE': settings.MNT_CURRENCY_CODE,
            'MNT_AMOUNT': order.invoice.amount,
            'MNT_DESCRIPTION': self.get_mnt_description(),
        }
        return '{}?{}'.format(settings.MONETA_TARGET_URL, urllib.urlencode(params))