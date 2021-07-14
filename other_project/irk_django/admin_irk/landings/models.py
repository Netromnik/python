# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime

from django.contrib.gis.db import models as geo_models
from django.db import models
from django.urls import reverse

from irk.gallery.fields import ManyToGallerysField
from irk.news.models import PostmetaMixin
from irk.obed.models import Establishment, Review
from irk.utils.decorators import memoized
from irk.utils.fields.file import FileRemovableField
from irk.utils.validators import FileSizeValidator


class DishQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(is_visible=True)

    def v2(self):
        return self.visible().filter(category__slug='v2')


class Resume(models.Model):
    """Резюме"""

    name = models.CharField('Имя', max_length=255)
    contact = models.CharField('Контакты', max_length=255)
    attach = FileRemovableField(verbose_name=u'Прикрепленный файл', upload_to='img/site/landings/attach/',
                                blank=True, null=True, validators=[FileSizeValidator(max_size=1024 * 1024 * 10)])
    link = models.CharField('Ссылка на резюме', max_length=255, default='', blank=True)
    content = models.TextField('Сообщение', default='', blank=True)
    created = models.DateTimeField('Время создания', auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'резюме'
        verbose_name_plural = 'резюме'


class TreasureDishCategory(models.Model):
    """Группа блюд, используется для создания независимых выпусков карты"""

    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Алиас', max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'категория гида'
        verbose_name_plural = 'категории гида'


class TreasureDish(models.Model):
    """Блюдо гастрономической карты"""

    is_visible = models.BooleanField('Показывать', default=False)
    name = models.CharField('Название', max_length=255)
    name_en = models.CharField('Английское название', max_length=255, default='', blank=True)
    establishment = models.ForeignKey(Establishment, verbose_name='Заведение', related_name='dishes')
    review = models.ForeignKey(Review, verbose_name='Рецензия', null=True)
    content = models.TextField('Описание', default='', blank=True)
    position = models.PositiveIntegerField('Позиция', default=0, db_index=True)
    rating = models.PositiveSmallIntegerField(default=0, help_text='от 1 до 3')

    category = models.ForeignKey(TreasureDishCategory, on_delete=models.SET_NULL, null=True,
                                 verbose_name='Категория', blank=True)
    gallery = ManyToGallerysField()

    objects = DishQuerySet.as_manager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'блюдо гастрономической карты'
        verbose_name_plural = 'блюда гастрономической карты'


class CovidPage(models.Model, PostmetaMixin):
    """
    Страница с информацией о коронавирусе

    У нас будет одна страница, контент которой будет обновляться и показываться
    на лендинге. Каждая карточка будет делаться бб-кодом ucard.

    UPD: информации стало слишком много, поэтому мы ввели карточки (ниже). Content
    разбивается на карточки скриптом create_covid_cards. Остаются только последние
    20, остальные конвертируются в объекты CovidCard.

    Можно было сразу сделать только CovidCard, но редакции нравится формат редактирования
    одного тектсового поля в CovidPage.
    """
    slug = models.SlugField('Алиас', default='main', max_length=100, unique=True)
    content = models.TextField('Текст', default='', blank=True)

    gallery = ManyToGallerysField()

    def __unicode__(self):
        return self.slug

    class Meta:
        verbose_name = 'COVID-19: Страница'
        verbose_name_plural = 'COVID-19: Страницы'

    def get_absolute_url(self):
        return reverse('landings_covid_index')


@memoized
def get_default_covid_page_id():
    page = CovidPage.objects.filter(slug='main').first()
    return page.pk if page.pk else None


class CovidCard(models.Model):
    page = models.ForeignKey(CovidPage, verbose_name='Страница о коронавирусе',
                             related_name='cards', default=get_default_covid_page_id)
    name = models.CharField('Заголовок', max_length=300)
    content = models.TextField('Содержание', default='', blank=True)
    created = models.DateTimeField('Дата', default=datetime.datetime.now)
    visible = models.BooleanField('Показывать', default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'COVID-19: Карточка'
        verbose_name_plural = 'COVID-19: Карточки'


class Article9May(models.Model):
    """
    Пост на карте для проекта 9 мая 2020
    """

    is_hidden = models.BooleanField('Скрытая', db_index=True, default=True)
    title = models.CharField('Заголовок', max_length=300)
    content = models.TextField('Содержание', blank=True)
    point = geo_models.PointField('Координата', default='', null=True, spatial_index=False)
    address = models.CharField('Адрес', max_length=255, default='', blank=True)

    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    gallery = ManyToGallerysField()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'Статья 9 мая'
        verbose_name_plural = 'Статьи 9 мая'


class Thank(models.Model):
    """
    Благодарности врачам
    """

    name = models.CharField('Имя', max_length=300)
    text = models.TextField('Текст')
    contact = models.CharField('Контактные данные', max_length=300)
    is_visible = models.BooleanField('Показывать', db_index=True, default=False)
    created = models.DateTimeField('Время добавления', editable=False, auto_now_add=True)
    updated = models.DateTimeField('Время редактирования', editable=False, auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Благодарность врачам'
        verbose_name_plural = 'Благодарности врачам'


class QuestionsGovernor(models.Model):
    """
    Вопрос губернатору
    """
    contact = models.CharField('Контактные данные', max_length=300)
    locality = models.CharField('Населенный пункт', max_length=300)
    text = models.TextField('Текст')
    created = models.DateTimeField('Время добавления', editable=False, auto_now_add=True)

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = 'Вопрос губернатору'
        verbose_name_plural = 'Вопросы губернатору'
