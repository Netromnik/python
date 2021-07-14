# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from irk.news.helpers import MaterialController


class Command(BaseCommand):
    help = u'Команда длф прегенерации списка новостей на главной раздела'

    def handle(self, **options):
        mc = MaterialController()
        mc.pregenerate_cache()
