# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import os

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.management.base import BaseCommand

from irk.landings.settings import PREDICTION_SOCIAL_CARD_PATH
from irk.landings.views.predictions import PREDICTION_DATA

PREDICTION_SOCIAL_CARD_BG = 'img/landing_pages/fortune_2020/social_card_bg.png'
PREDICTION_SOCIAL_CARD_FONT = 'static/font/pt-sans/PT_Sans_Bold.ttf'
PREDICTION_SOCIAL_CARD_FULL_PATH = os.path.join(settings.MEDIA_ROOT, PREDICTION_SOCIAL_CARD_PATH)
TEXT_CENTER = (422, 305)


class Command(BaseCommand):
    """Сгенерировать соцкарточки для предсказаний"""

    def handle(self, *args, **options):

        if not os.path.exists(PREDICTION_SOCIAL_CARD_FULL_PATH):
            os.makedirs(PREDICTION_SOCIAL_CARD_FULL_PATH)

        for idx, text in PREDICTION_DATA.items():
            img_path = find(PREDICTION_SOCIAL_CARD_BG)
            img = Image.open(img_path)

            font_path = os.path.join(settings.BASE_DIR, PREDICTION_SOCIAL_CARD_FONT)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(font_path, 30)

            # Определение координаты текста
            text_width, text_height = draw.textsize(text, font)
            text_position_width = int(TEXT_CENTER[0] - (text_width / 2))
            text_position_height = int(TEXT_CENTER[1] - (text_height / 2))

            draw.multiline_text((text_position_width, text_position_height), text,
                                fill='#3a2d8a', font=font, align='center')

            social_card_img = os.path.join(PREDICTION_SOCIAL_CARD_FULL_PATH, '{}.png'.format(idx))
            img.save(social_card_img)
