# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import operator
import os
import tarfile

import geoip2.database
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from irk.polls.models import Poll, PollChoice, PollVote
from irk.utils.helpers import inttoip

GEOIP_DB_URL = 'https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'
GEOIP_DB_FILE = 'GeoLite2-City.mmdb'
GEOIP_DB_PATH = os.path.join(settings.MEDIA_ROOT, GEOIP_DB_FILE)


class Command(BaseCommand):
    """Комманда для провеки накрутки в голосованиях"""

    def add_arguments(self, parser):
        parser.add_argument('poll_id', help='id голосования', type=int)
        parser.add_argument('choice_id', help='id выбора', nargs='?', type=int)

    def handle(self, *args, **options):
        poll_id = options['poll_id']
        choice_id = options['choice_id']

        # Скачать файл с базой если его не существует
        if not os.path.exists(GEOIP_DB_PATH):
            print('Downloading db file...')

            r = requests.get(GEOIP_DB_URL, allow_redirects=True)
            archive_name = '{}.tar.gz'.format(GEOIP_DB_PATH)
            open(archive_name, 'wb').write(r.content)
            tf = tarfile.open(archive_name)

            for member in tf.getmembers():
                if member.name.endswith('mmdb'):
                    member.name = GEOIP_DB_FILE
                    tf.extract(member, settings.MEDIA_ROOT)
                    os.remove(archive_name)

        if not choice_id:

            poll = Poll.objects.get(id=poll_id)

            choices = PollChoice.objects.filter(poll=poll).order_by('votes_cnt')

            print('id\tvotes\tname')
            for choice in choices:
                print('{}\t{}\t{}'.format(choice.pk, choice.votes_cnt, choice.text))

        else:
            reader = geoip2.database.Reader(GEOIP_DB_PATH)

            choice = PollChoice.objects.get(pk=choice_id)
            print('{}'.format(choice.text))

            votes = PollVote.objects.filter(choice=choice).order_by('id')
            votes_count = votes.count()
            print('всего голосов {}'.format(votes_count))

            user_votes_count = votes.filter(user__isnull=False).count()
            print('от пользователей {}'.format(user_votes_count))

            data = {}

            for vote in votes:
                ip = inttoip(vote.ip)
                try:
                    response = reader.city(ip)

                    if response.country.name not in data:
                        data[response.country.name] = {}
                    if response.city.name not in data[response.country.name]:
                        data[response.country.name][response.city.name] = 0

                    data[response.country.name][response.city.name] += 1

                    # print ' new google.maps.LatLng({}, {}),'.format(response.location.latitude,
                    # response.location.longitude)
                except:
                    pass

            for country, row in data.items():
                print('- {}'.format(country))
                for city, votes_cnt in sorted(row.items(), key=operator.itemgetter(1), reverse=True):
                    print('{} {}'.format(votes_cnt, city))

            for i, vote in enumerate(votes):
                try:
                    response = reader.city(inttoip(vote.ip))
                except:
                    pass
                print('{}) {}, {}, {}'.format(i, vote.created, inttoip(vote.ip), response.city.name))
