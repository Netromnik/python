# -*- coding: utf-8 -*-

import datetime


from django.core.management.base import BaseCommand

from irk.news.models import Article


class Command(BaseCommand):
    """Снять просроченные галочки оплаченных статей"""

    def handle(self, *args, **options):

        Article.objects.filter(is_paid=True, paid__lte=datetime.datetime.now() - datetime.timedelta(hours=24)).\
            update(is_paid=False, paid=None)
