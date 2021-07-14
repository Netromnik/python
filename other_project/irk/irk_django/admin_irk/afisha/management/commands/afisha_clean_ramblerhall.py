# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from irk.afisha.models import RamblerHall, RamblerSession


class Command(BaseCommand):
    """ Удаление не привязанных залов"""

    def handle(self, *args, **options):
        hall_qs = RamblerHall.objects.filter(hall_id__isnull=True)
        hall_ids = hall_qs.values_list('pk', flat=True)

        RamblerSession.objects.filter(hall_id__in=hall_ids).delete()
        hall_qs.delete()
