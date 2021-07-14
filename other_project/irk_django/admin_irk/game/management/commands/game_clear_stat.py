# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand

from irk.game.models import Progress, Purchase


class Command(BaseCommand):
    """
    Удаляет статистику всех игроков не взявшых призы для того чтобы на следующий день розыгрыша они начали заново
    """

    help = 'Очистка игровой статистики'

    def handle(self, *args, **options):
        gamer_ids = Purchase.objects.all().values_list("gamer_id", flat=True)
        Progress.objects.exclude(gamer_id__in=gamer_ids).delete()