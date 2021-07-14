from invoice.order_helpers import BaseOrderHelper
from utils.notifications import tpl_notify

from .models import AdvOrder
from .permissions import get_moderators


class AdvOrderHelper(BaseOrderHelper):
    """Управление заказами на размещение рекламы"""

    order_class = AdvOrder

    def __init__(self, advorder=None, request=None):
        self.advorder = advorder
        self.request = request

    def get_order(self):
        return self.advorder

    def create_order(self, *args, **kwargs):
        order = super(AdvOrderHelper, self).create_order(*args, **kwargs)
        self.send_new(order)
        return order

    def send_new(self, order):
        """Отправить уведомление о новом заказе"""

        tpl_notify('Заказ на размещение', 'adv/notif/new.html', {'order': order},
                   emails=get_moderators().values_list('email', flat=True))

    def send_rejection(self):
        """Отправить уведомление об отказе"""

        order = self.get_order()

        context = {
            'order': order,
        }

        tpl_notify(self.get_mnt_description(), 'adv/notif/rejection.html', context,
                   emails=[order.client_email, ])

    def send_invoice(self):
        """Отправить ссылку на оплату по почте"""

        order = self.get_order()

        context = {
            'url': self.get_invoice_url(),
            'order': order,
        }

        tpl_notify(self.get_mnt_description(), 'adv/notif/invoice.html', context,
                   emails=[order.client_email, ])

    def get_mnt_description(self):
        return 'Оплата размещения услуги "{}"'.format(self.advorder.service.name).encode('utf8')

    @staticmethod
    def invoice_success_status(invoice):
        """Уведомить об оплате"""

        order = invoice.order_invoice.content_object

        tpl_notify('Клиет оплатил заказ', 'adv/notif/paid.html', {'order': order},
            emails=get_moderators().values_list('email', flat=True))
