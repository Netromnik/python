# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User

from django.core.management.base import BaseCommand
from irk.newyear2014.models import Congratulation


class Command(BaseCommand):

    def handle(self, *args, **options):

        for congratulation in Congratulation.objects.all():
            if congratulation.sign.startswith('irk'):
                try:
                    congratulation.sign = congratulation.user.profile.full_name
                    congratulation.save()
                except User.DoesNotExist:
                    pass

