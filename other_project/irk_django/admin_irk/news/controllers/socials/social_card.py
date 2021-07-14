# -*- coding: utf-8 -*-

"""
Модуль содержит классы создателей социальных карточек для различных видов материалов.
"""

import io
import os

from PIL import Image, ImageDraw, ImageFont

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.files.base import ContentFile
from django.template.defaultfilters import wordwrap

import irk.news.settings as app_settings
from irk.utils.text.processors.default import processor


class SocialCardCreator(object):
    """
    Создатель социальных каточек.

    Содержит методы для рисования основных элементов карточки.
    Алгоритм рисования определяет метод _create_image, он абстрактный и должен быть реализован в подклассах.
    """

    # Размеры социальной карточки
    width = 845
    height = 445

    # Цвет текста
    text_color = '#fff'
    # Цвет фона
    background = '#0095fc'

    def __init__(self, instance):
        """
        :param SocialCardMixin instance: объект для которого создается социальная карточка
        """

        self._instance = instance
        self._social_card = None
        # Объект рисования
        self._draw = None

        self._font_path = os.path.join(settings.BASE_DIR, 'static/font/pt-sans/PT_Sans_Bold.ttf')

    def create(self):
        """Создать социальную карточку для материала"""

        self._create_image()
        self._save_social_card()

        return self._social_card

    def _create_image(self):
        """Создать изображение карточки"""

        # реализация в подклассах
        raise NotImplementedError

    def _draw_text(self, color):
        """Нарисовать текст"""

        kwargs = {
            'replace_links': False,
            'strip_bb_codes': True,
            'replace_smiles': False,
            'escape_html': False,
        }

        margin_left = 30
        margin_bottom = 103
        font_size = 55

        text = processor.format(self._instance.social_text, **kwargs).strip()
        text = self._split_lines(text)

        draw = ImageDraw.Draw(self._social_card)

        font = ImageFont.truetype(self._font_path, font_size)
        text_w, text_h = draw.multiline_textsize(text, font=font, spacing=0)
        y = self.height - text_h - margin_bottom
        draw.multiline_text((margin_left, y), text, fill=color, font=font, spacing=0)

    def _draw_logo(self):
        """Нарисовать логотип"""

        logo_path = os.path.join(settings.BASE_DIR, 'static/img/social_cards/logo.png')

        logo = Image.open(logo_path)
        margin_left = 30
        margin_top = 30

        # Для учета канала прозрачности необходимо использовать mask
        self._social_card.paste(logo, box=(margin_left, margin_top), mask=logo)

    def _draw_label(self):
        """Нарисовать метку статьи"""

        text = self._instance.get_social_label()
        if not text:
            return

        self._draw_splitter()

        font_size = 20
        font = ImageFont.truetype(self._font_path, font_size)
        color = '#fff'

        margin_left = 126
        margin_top = 29

        self._draw.text((margin_left, margin_top), text, fill=color, font=font)

    def _draw_splitter(self):
        """Нарисовать разделитель лого и лэйбла"""

        splitter_path = os.path.join(settings.BASE_DIR, 'static/img/social_cards/splitter.png')
        splitter = Image.open(splitter_path)

        margin_left = 105
        margin_top = 24

        self._social_card.paste(splitter, box=(margin_left, margin_top), mask=splitter)

    def _save_social_card(self):
        """Сохранить изображение в качестве социальной карточки материала"""

        buf = io.BytesIO()
        self._social_card.save(buf, 'png')

        self._instance.social_card.save('social_card.png', ContentFile(buf.getvalue()), save=False)

    @staticmethod
    def _split_lines(text):
        """
        Разбить текст на строки.
        Если строка всего одна, она разбивается автоматически на строки по 26 символов.

        :param unicode text: текст
        """

        lines = text.splitlines()

        if len(lines) == 1:
            lines = wordwrap(lines[0], 26).splitlines()

        return u'\n'.join(lines)


class PlainSocialCardCreator(SocialCardCreator):
    """Создатель социальных карточек с одноцветным фоном"""

    background = '#0095fc'

    def _create_image(self):
        """Создать изображения для новости"""

        self._social_card = Image.new('RGB', (self.width, self.height), self.background)

        self._draw = ImageDraw.Draw(self._social_card)
        self._draw_logo()
        self._draw_label()
        self._draw_text(self.text_color)


class BackgroundSocialCardCreator(SocialCardCreator):
    """Создатель социальных карточек с графическим фоном"""

    background = '#000'
    # Прозрачность фонового изображения. Используется при наложении фотографий
    background_alpha = 0.4

    def _create_image(self):
        """Создать изображение для статьи"""

        self._social_card = Image.new('RGB', (self.width, self.height), self.background)
        self._blend_background()

        self._draw = ImageDraw.Draw(self._social_card)
        self._draw_logo()
        self._draw_label()
        self._draw_text(self.text_color)

    def _blend_background(self):
        """
        Наложить фоновое изображение

        Для наложения требуется, чтобы изображения совпадали по размерам и цветовому режиму, если это не так, код
        пытается привести фоновое изображение в соответствие с социальной карточкой.
        """

        # Фоновое изображение для социальной карточки
        background_image = None
        if self._instance.social_image:
            background_image = self._image_from_field(self._instance.social_image)
        # Пробуем использовать широкоформатную фотографию
        elif self._instance.wide_image:
            background_image = self._image_from_field(self._instance.wide_image)

        if not background_image:
            return

        prepared_image = self._prepare_for_blend(background_image)
        self._social_card = Image.blend(self._social_card, prepared_image, self.background_alpha)

    def _prepare_for_blend(self, background_image):
        """
        Подготовить фоновое изображение для совмещения с карточкой

        :param Image.Image background_image: фоновое изображение
        :return: объект фонового изображения пригодный к совмещению
        :rtype: Image.Image
        """

        if background_image.size != self._social_card.size:
            w, h = background_image.size
            background_image = background_image.crop([w - self.width, h - self.height, w, h])

        if background_image.mode != self._social_card.mode:
            background_image = background_image.convert(self._social_card.mode)

        return background_image

    @staticmethod
    def _image_from_field(image_field):
        """
        Получить изображение из поля модели

        :param django.db.models.ImageField image_field: поле модели содержащее изображение
        :return: объект изображения
        :rtype: Image.Image or None
        """

        try:
            # По каким-то причинам PIL.Image не может идентифицировать изображение, когда оно 1й раз загружается
            # Устанавливаем курсор файла на начало, чтобы избежать этой ошибки.
            image_field.seek(0)
            return Image.open(image_field)
        except IOError:
            return None


class SubjectSocialCardCreator(PlainSocialCardCreator):
    background = '#002959'


class VideoSocialCardCreator(PlainSocialCardCreator):
    background = '#464642'

    def _draw_label(self):
        self._draw_splitter()

        path = os.path.join(settings.BASE_DIR, 'static/img/social_cards/label_video.png')

        label = Image.open(path)
        margin_left = 143
        margin_top = 30

        # Для учета канала прозрачности необходимо использовать mask
        self._social_card.paste(label, box=(margin_left, margin_top), mask=label)


class PodcastSocialCardCreator(BackgroundSocialCardCreator):
    """Creator social card for Podcast"""

    def _blend_background(self):
        """
        Наложить фоновое изображение

        Для наложения требуется, чтобы изображения совпадали по размерам и цветовому режиму, если это не так, код
        пытается привести фоновое изображение в соответствие с социальной карточкой.
        """

        # Фоновое изображение для социальной карточки
        path = find(app_settings.PODCAST_SOCIAL_CARD_IMAGE)
        try:
            background_image = Image.open(path)
        except IOError:
            return

        prepared_image = self._prepare_for_blend(background_image)
        self._social_card = Image.blend(self._social_card, prepared_image, self.background_alpha)
