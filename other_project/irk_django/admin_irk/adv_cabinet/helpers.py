# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals


def get_ba_clients(request):
    """Получить список привязанных к бизнес аккаунту клиентов"""

    return request.user.profile.business_account.clients.filter(is_deleted=False, is_active=True)
