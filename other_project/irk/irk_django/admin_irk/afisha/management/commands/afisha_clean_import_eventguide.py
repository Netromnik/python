# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from irk.afisha.models import EventGuide


class Command(BaseCommand):
    """ Очистка всех EventGuide созданных автоматически"""

    def handle(self, *args, **options):
        if not EventGuide.objects.filter(
                source__in=[EventGuide.SOURCE_KINOMAX, EventGuide.SOURCE_RAMBLER]).exists():
            # Удаляются EventGuide всех импортируемых кинотеатров кроме Карамели
            # (в настоящий момент Рамблер не отдает сеансы Карамели)
            EventGuide.objects.filter(guide__in=[24354, 84, 88, 1226, 21867, 24294, 24307]).delete()
