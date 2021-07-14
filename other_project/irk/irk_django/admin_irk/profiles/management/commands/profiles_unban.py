# -*- coding: utf-8 -*-

"""Разбаниваем пользователей, у которых закончился срок бана"""

import datetime

from django.core.management.base import BaseCommand

from irk.profiles.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        Profile.objects.filter(is_banned=True, bann_end__isnull=False,
                               bann_end__lt=datetime.datetime.now()).update(is_banned=False)
