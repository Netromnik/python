# -*- coding: utf-8 -*-

"""Удаление данных по завершившимся более чем месяц назад голосованиям"""

import datetime

from django.core.management.base import BaseCommand

from irk.polls.models import Poll, PollVote


class Command(BaseCommand):
    def handle(self, *args, **options):
        for poll in Poll.objects.filter(end__lt=datetime.date.today() - datetime.timedelta(days=30)):
            PollVote.objects.filter(choice__in=poll.choices.all()).delete()
