# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from urlparse import urljoin

from django.core.management.base import BaseCommand

from irk.landings.models import CovidPage
from irk.news.models_postmeta import Postmeta
from irk.utils.grabber import proxy_requests


API_URL = 'https://coronavirus-19-api.herokuapp.com/'
WORLD_DATA_PATH = 'all/'
RUSSIA_DATA_PATH = 'countries/russia/'


class Command(BaseCommand):
    """Получить данные о зараженных covid для лендинга"""

    def grab_world_data(self):
        url = urljoin(API_URL, WORLD_DATA_PATH)

        response = proxy_requests.get(url)
        response.raise_for_status()

        return response.json()

    def grab_russia_data(self):
        url = urljoin(API_URL, RUSSIA_DATA_PATH)

        response = proxy_requests.get(url)
        response.raise_for_status()

        return response.json()

    def rounding(self, value):
        if value > 999999:
            value = '{}М'.format(round(float(value) / 1000000, 1))
        elif value > 999:
            value = '{}К'.format(int(round(float(value) / 1000)))
        return value

    def handle(self, *args, **options):

        world_data = self.grab_world_data()
        russia_data = self.grab_russia_data()

        key_map = {
            'ru_cases': self.rounding(russia_data['cases']),
            'ru_deaths': self.rounding(russia_data['deaths']),
            'ru_recovered': self.rounding(russia_data['recovered']),
            'world_cases': self.rounding(world_data['cases']),
            'world_deaths': self.rounding(world_data['deaths']),
            'world_recovered': self.rounding(world_data['recovered']),
        }

        page = CovidPage.objects.get(slug='main')

        for key, value in key_map.items():
            postmeta = Postmeta.objects.get(landings_covidpage=page, key=key)
            postmeta.value = value
            postmeta.save()
