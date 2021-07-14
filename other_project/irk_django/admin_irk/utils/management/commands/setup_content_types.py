# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.management import update_all_contenttypes
# Add any missing content types

from django.contrib.auth.management import create_permissions
from django.db.models import get_apps


class Command(BaseCommand):
    help = u"Обновляет данные таблицы content_types."
    args = ""

    def handle(self, *args, **options):
        update_all_contenttypes(interactive=True)
        for app in get_apps():
            create_permissions(app, None, 2)
