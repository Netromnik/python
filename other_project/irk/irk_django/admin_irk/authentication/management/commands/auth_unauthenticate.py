# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from irk.authentication.helpers import deauth_users

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Деавторизация пользователей путем удаления их сессии"""

    def handle(self, *user_ids, **options):
        deauth_users(user_ids)
