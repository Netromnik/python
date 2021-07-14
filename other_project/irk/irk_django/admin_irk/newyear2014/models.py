# -*- coding: utf-8 -*-

import os
import uuid
import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

from irk.utils.fields.file import ImageRemovableField
from irk.gallery.fields import ManyToGallerysField as GalleryField
from irk.news import models as news_models
from irk.news.models import material_register_signals


class Congratulation(models.Model):
    """Поздравление"""

    content = models.TextField(u'Текст')
    sign = models.CharField(u'Подпись', max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'Автор поздравления',
                             related_name='congratulation')
    created = models.DateTimeField(editable=False, auto_now_add=True)
    is_hidden = models.BooleanField(u'Скрытое', default=False)

    class Meta:
        verbose_name = u'поздравление'
        verbose_name_plural = u'поздравления'

    def __unicode__(self):
        return self.content

    def should_be_truncated(self):
        return len(self.content) > 185


class Wish(models.Model):
    """Желание"""

    content = models.TextField(u'Текст')
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'Автор желания', related_name='wish')
    created = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        verbose_name = u'желание'
        verbose_name_plural = u'желания'

    def __unicode__(self):
        return self.content


# TODO ненужна
class Question(models.Model):
    """Вопросы к гаданию"""

    content = models.TextField(u'Текст')
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'Автор вопроса',
                             related_name='prediction_question')
    created = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        verbose_name = u'вопрос к гаданию'
        verbose_name_plural = u'вопросы к гаданию'

    def __unicode__(self):
        return self.content


class Prediction(models.Model):
    """Ответы для гадания"""

    content = models.CharField(u'Текст', max_length=255)

    class Meta:
        verbose_name = u'ответ для гадания'
        verbose_name_plural = u'ответы для гадания'

    def __unicode__(self):
        return self.content


class Horoscope(models.Model):
    """Гороскоп"""

    name = models.CharField(u'Название', max_length=255)
    short_name = models.CharField(u'Короткое название', max_length=255, null=True, blank=True)
    position = models.PositiveIntegerField(u'Позиция', default=0)
    content = models.TextField(u'Содержание')

    class Meta:
        verbose_name = u'гороскоп'
        verbose_name_plural = u'гороскопы'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('newyear2014.views.horoscope.read', args=(self.pk, ))


class Zodiac(models.Model):
    """Знак зодиака"""

    name = models.CharField(u'Название', max_length=255)
    horoscope = models.ForeignKey(Horoscope, verbose_name=u'Гороскоп')
    content = models.TextField(u'Содержание')
    position = models.PositiveIntegerField(u'Позиция', default=0)
    image = ImageRemovableField(upload_to='img/site/newyear2014/horoscope/', verbose_name=u'Изображение')

    class Meta:
        verbose_name = u'знак зодиака'
        verbose_name_plural = u'знаки зодиака'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('newyear2014.views.horoscope.zodiac_read', args=(self.pk, ))


def offer_image_upload_to(instance, filename):
    return 'img/site/newyear2014/offers/%(filename)s.%(ext)s' % {
        'filename': str(uuid.uuid4()),
        'ext': os.path.splitext(filename)[1].lstrip('.').lower(),
    }


class Offer(models.Model):
    """Лучшие предложения"""

    date_start = models.DateField(u'Дата начала показа', db_index=True)
    date_end = models.DateField(u'Дата окончания показа', db_index=True)
    title = models.CharField(u'Название', max_length=255)
    caption = models.TextField(u'Подводка')
    content = models.TextField(u'Описание')
    image = ImageRemovableField(verbose_name=u'Фотография', blank=True, upload_to=offer_image_upload_to)  #  max_size=(1600, 1200)
    url = models.URLField(u'Ссылка', blank=True, null=True)

    gallery = GalleryField()

    class Meta:
        verbose_name = u'лучшее предложение'
        verbose_name_plural = u'лучшие предложения'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('newyear2014.views.offers.read', args=(self.pk, ))


# Конкурсы

def contest_image_upload_to(instance, filename):
    return 'img/site/newyear2014/contests/%(filename)s.%(ext)s' % {
        'filename': str(uuid.uuid4()),
        'ext': os.path.splitext(filename)[1].lstrip('.').lower(),
    }


def contest_sponsor_upload_to(instance, filename):
    return 'img/site/newyear2014/contests/sponsor/%(filename)s.%(ext)s' % {
        'filename': str(uuid.uuid4()),
        'ext': os.path.splitext(filename)[1].lstrip('.').lower(),
    }


class TextContest(models.Model):
    title = models.CharField(u'Название', max_length=255)
    caption = models.TextField(u'Подводка')
    content = models.TextField(u'Описание')
    image = ImageRemovableField(verbose_name=u'Фотография',blank=True, upload_to=contest_image_upload_to) #  max_size=(1600, 1200)
    date_start = models.DateField(u'Дата начала проведения', db_index=True)
    date_end = models.DateField(u'Дата окончания проведения', db_index=True)
    sponsor_title = models.CharField(u'Название спонсора', max_length=255, null=True, blank=True)
    sponsor_image = ImageRemovableField(verbose_name=u'Картинка спонсора', null=True, blank=True,
                                     upload_to=contest_sponsor_upload_to) # max_size=(80, 80),
    is_blocked = models.BooleanField(default=False, verbose_name=u'Закрыть голосование',
                                     help_text=u'Голосование отображается, но возможность проголосовать отключена')
    user_can_add = models.BooleanField(verbose_name=u'Пользователи могут добавляться', default=True)

    class Meta:
        verbose_name = u'текстовый конкурс'
        verbose_name_plural = u'текстовые конкурсы'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('newyear2014.views.contests.text.read', args=(self.id, ))

    @property
    def can_rate(self):
        if self.date_end >= datetime.date.today() and not self.is_blocked:
            return True
        else:
            return False


class TextContestParticipant(models.Model):
    """Участник текстового конкурса

    Может быть как авторизированным, так и анонимным
    """

    contest = models.ForeignKey(TextContest, related_name='participants')
    user = models.ForeignKey(User, related_name='text_contests', null=True, blank=True)
    is_visible = models.BooleanField(u'Отображается', db_index=True, default=True)
    name = models.CharField(u'Имя', max_length=255)
    email = models.EmailField(u'E-mail', blank=True)
    title = models.CharField(u'Название', max_length=255)
    content = models.TextField(u'Текст')

    class Meta:
        verbose_name = u'участник текстового конкурса'
        verbose_name_plural = u'участники текстового конкурса'

    def get_absolute_url(self):
        return reverse('newyear2014.views.contests.text.participant', args=(self.contest_id, self.id, ))

    def __unicode__(self):
        return self.name


class PhotoContest(models.Model):
    """Фотоконкурс"""

    title = models.CharField(u'Название', max_length=255)
    caption = models.TextField(u'Подводка')
    content = models.TextField(u'Описание')
    image = ImageRemovableField(verbose_name=u'Фотография', blank=True, upload_to=contest_image_upload_to) # max_size=(1600, 1200),
    date_start = models.DateField(u'Дата начала проведения', db_index=True)
    date_end = models.DateField(u'Дата окончания проведения', db_index=True)
    sponsor_title = models.CharField(u'Название спонсора', max_length=255, null=True, blank=True)
    sponsor_image = ImageRemovableField(verbose_name=u'Картинка спонсора', null=True, blank=True,
                                     upload_to=contest_sponsor_upload_to)  # max_size=(80, 80)
    is_blocked = models.BooleanField(default=False, verbose_name=u'Закрыть голосование',
                                     help_text=u'Голосование отображается, но возможность проголосовать отключена')
    user_can_add = models.BooleanField(verbose_name=u'Пользователи могут добавляться', default=True)

    class Meta:
        verbose_name = u'фотоконкурс'
        verbose_name_plural = u'фотоконкурсы'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('newyear2014.views.contests.photo.read', args=(self.id, ))

    @property
    def can_rate(self):
        if self.date_end >= datetime.date.today() and not self.is_blocked:
            return True
        else:
            return False


def contest_participant_image_upload_to(instance, filename):
    return 'img/site/newyear2014/contests/photo/%(filename)s.%(ext)s' % {
        'filename': str(uuid.uuid4()),
        'ext': os.path.splitext(filename)[1].lstrip('.').lower(),
    }


class PhotoContestParticipant(models.Model):
    """Участник фотоконкурса

    Может быть как авторизированным, так и анонимным
    """

    contest = models.ForeignKey(PhotoContest, related_name='participants')
    user = models.ForeignKey(User, related_name='photo_contests', null=True, blank=True)
    is_visible = models.BooleanField(u'Отображается', db_index=True, default=True)
    name = models.CharField(u'Имя', max_length=255)
    email = models.EmailField(u'E-mail', blank=True)
    title = models.CharField(u'Название', max_length=255)
    image = ImageRemovableField(upload_to=contest_participant_image_upload_to)
    content = models.TextField(u'Текст')

    class Meta:
        verbose_name = u'участник фотоконкурса'
        verbose_name_plural = u'участники фотоконкурса'

    def get_absolute_url(self):
        return reverse('newyear2014.views.contests.photo.participant', args=(self.contest_id, self.id, ))

    def __unicode__(self):
        return self.name


# Обои на рабочий стол

def wallpaper_image_upload_to(instance, filename):
    return 'img/site/newyear2014/wallpapers/%(filename)s.%(ext)s' % {
        'filename': str(uuid.uuid4()),
        'ext': os.path.splitext(filename)[1].lstrip('.').lower(),
    }


class Wallpaper(models.Model):
    title = models.CharField(u'Название', max_length=255)
    standard_image = ImageRemovableField(upload_to=wallpaper_image_upload_to, verbose_name=u'Изображение', 
                                      help_text=u'Изображение размером 1280x1024')  # max_size=(1280, 1024)
    wide_image = ImageRemovableField(upload_to=wallpaper_image_upload_to, verbose_name=u'Широкоформатное изображение',
                                  help_text=u'Изображение размером 1920x1080')

    class Meta:
        verbose_name = u'обои'
        verbose_name_plural = u'обои'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('newyear2014.views.wallpapers.read', args=(self.id, ))


def puzzle_image_upload_to(instance, filename):
    return 'img/site/newyear2014/puzzle/%(filename)s.%(ext)s' % {
        'filename': str(uuid.uuid4()),
        'ext': os.path.splitext(filename)[1].lstrip('.').lower(),
    }


class Puzzle(models.Model):
    title = models.CharField(u'Название', max_length=255)
    image = ImageRemovableField(upload_to=wallpaper_image_upload_to, verbose_name=u'Изображение')
    url = models.CharField(u'Ссылка на фото в фоторепортаже', max_length=100, blank=True, null=True,
                           help_text=u'Например: /news/photo/20130917/holiday/#event=312990')

    class Meta:
        verbose_name = u'пазл'
        verbose_name_plural = u'пазлы'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('newyear2014.views.puzzle.read', args=(self.id, ))


class GuruAnswer(models.Model):
    """Ответы """

    GENDER_MALE = 'm'
    GENDER_FEMALE = 'f'
    GENDER_CHOICES = (
        (GENDER_MALE, u'мужской'),
        (GENDER_FEMALE, u'женский')
    )

    AGE_UNDER_30 = 'lt30'
    AGE_AFTER_30 = 'gt30'
    AGE_CHOICES = (
        (AGE_UNDER_30, u'младше 30'),
        (AGE_AFTER_30, u'старше 30')
    )

    content = models.TextField(u'Текст')
    gender = models.CharField(u'Пол', max_length=1, choices=GENDER_CHOICES, db_index=True)
    age = models.CharField(u'Возраст', max_length=10, choices=AGE_CHOICES, db_index=True)

    class Meta:
        verbose_name = u'ответ как встретить НГ'
        verbose_name_plural = u'ответы как встретить НГ'

    def __unicode__(self):
        return self.content


@material_register_signals
class Infographic(news_models.Infographic):
    class Meta:
        proxy = True
        verbose_name = u'инфографика'
        verbose_name_plural = u'инфографика раздела'


@material_register_signals
class Article(news_models.Article):
    class Meta:
        proxy = True
        verbose_name = u'статья'
        verbose_name_plural = u'статьи раздела'


@material_register_signals
class Photo(news_models.Photo):
    class Meta:
        proxy = True
        verbose_name = u'фоторепортаж'
        verbose_name_plural = u'фоторепортажи раздела'
