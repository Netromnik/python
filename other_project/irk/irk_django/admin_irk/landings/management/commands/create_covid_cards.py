# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import re

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from irk.gallery.models import Gallery, GalleryPicture
from irk.landings.models import CovidCard, CovidPage

MONTH_NAMES = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}

KEEP_CARD_COUNT = 20

class Command(BaseCommand):
    """Разбить текст страницы covid на отдельные карточки"""

    def handle(self, *args, **options):
        page = CovidPage.objects.get(slug='main')
        text = page.content

        ucards_re = re.compile(r'''\[ucard\s+supheader="(.*?)"\s*title="(.*?)"\](.*?)\[\/ucard\]''', re.DOTALL)
        image_re = re.compile(r'''\[image\s+(\d*)\]''', re.DOTALL)

        covid_card_ct = ContentType.objects.get_for_model(CovidCard)

        ucards = ucards_re.findall(text)
        for ucard in ucards[::-1][:-KEEP_CARD_COUNT]:

            chunks = ucard[0].split()
            day = chunks[0]
            month = chunks[1]
            month = MONTH_NAMES[month]

            now = datetime.datetime.now()
            year = now.year
            # Для прошлогодних карточек ставим предидущий год
            if now.month < month:
                year -= 1

            date = datetime.datetime(year=year, month=month, day=int(day))
            content = ucard[2].strip()
            name = ucard[1].strip()

            card = CovidCard()
            card.content = content
            card.name = name
            card.created = date
            card.visible = True
            card.save()

            images = image_re.findall(content)
            for position, image_id in enumerate(images, start=1):
                gallery, created = Gallery.objects.get_or_create(object_id=card.pk, content_type=covid_card_ct)
                gallery_picture = GalleryPicture.objects.get(pk=image_id)
                gallery_picture.gallery_id = gallery.pk
                gallery_picture.position = position
                gallery_picture.save()

            # Удаление последней карточки из текста
            ucard_end_position = text.rfind('[ucard')
            text = text[:ucard_end_position]
            page.content = text
            page.save()
