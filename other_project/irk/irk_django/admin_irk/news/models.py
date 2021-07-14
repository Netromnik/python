# -*- coding: utf-8 -*-

import binascii
import datetime
import logging
import os.path
import random
import re
import shutil
import uuid

from dateutil import rrule
from django.conf import settings
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.finders import find
from django.contrib.gis.db import models as geo_models
from django.core.cache import cache
from django.core.files import File
from django.core.urlresolvers import NoReverseMatch, reverse, reverse_lazy
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_delete, post_save, pre_save

import irk.news.settings as app_settings
from irk.authentication.helpers import get_hexdigest
from irk.comments.models import CommentMixin
from irk.gallery.fields import ManyToGallerysField
from irk.news import search, signals
from irk.news.cache import invalidate
from irk.news.managers import (
    BaseMaterialManager, BaseNewsletterManager, LongreadMaterialManager, MagazineMaterialManager, MaterialManager,
)

from irk.news.models_postmeta import Postmeta, PostmetaMixin  # pylint: disable=unused-import
from irk.options.helpers import CurrentSite
from irk.options.models import Site
from irk.scheduler.models import Task
from irk.special.models import Project
from irk.utils.fields.file import FileRemovableField, ImageRemovableField
from irk.utils.helpers import big_int_from_time, int_or_none
from irk.utils.managers import TaggableManager
from irk.utils.tilda import IrkruTildaArchive

logger = logging.getLogger(__name__)

# Типы новостей
NEWS_TYPES = (
    ('news', 'Новость'),
    ('article', 'Статья'),
    ('foto', 'Фоторепортаж'),
    ('video', 'Видео'),
)

MEDIA_EXTENSIONS = ['gif', 'jpg', 'jpeg', 'png', 'bmp', 'tif',
                    'mp4', 'avi', 'mkv', '3gp', 'mov', 'webm', 'm4v', 'mpeg']


def wide_image_upload_to(instance, filename):
    """Вернуть путь для сохранения широкоформатной фотографии"""

    opts = instance._meta

    return 'img/site/news/{model_name}/{folder}/{filename}{ext}'.format(
        model_name=opts.model_name,
        folder=opts.model.objects.count() / 1024,
        filename=str(uuid.uuid4()),
        ext=os.path.splitext(filename)[1],
    )


def social_card_upload_to(instance, filename):
    return 'img/site/news/material/social/{folder}/{filename}{ext}'.format(
        folder=BaseMaterial.objects.count() / 1024,
        filename=str(uuid.uuid4()),
        ext=os.path.splitext(filename)[1],
    )


def social_pult_upload_to(instance, filename):
    name = binascii.hexlify(os.urandom(4))  # ex: '3266db8e'
    return 'img/site/news/social_pult/{folder}/{name}{ext}'.format(
        folder=BaseMaterial.objects.count() / 1024,
        name=name,
        ext=os.path.splitext(filename)[1],
    )


def category_image_upload_to(instance, filename):
    return 'img/site/news/categories/%(filename)s.%(ext)s' % {
        'filename': str(uuid.uuid4()),
        'ext': os.path.splitext(filename)[1].lstrip('.'),
    }


def tilda_upload_to(instance, filename):
    return 'img/site/news/tilda/{year}/{filename}'.format(
        year=datetime.datetime.today().year,
        filename=filename,
    )


def material_register_signals(model_cls):
    """Декоратор для регистрации материалов"""
    post_save.connect(invalidate, sender=model_cls)
    post_delete.connect(invalidate, sender=model_cls)

    return model_cls


class SocialCardMixin(models.Model):
    """Примесь для моделей, имеющих социальную карточку"""

    social_image = ImageRemovableField(
        verbose_name=u'Фон карточки', upload_to=social_card_upload_to, blank=True, null=True,
        help_text=u'Размер 940x445'
    ) #  min_size=(940, 445), max_size=(940, 445)
    social_text = models.CharField(u'Текст карточки', max_length=100, blank=True, help_text=u'100 знаков')
    social_label = models.CharField(u'Метка', max_length=50, blank=True, help_text=u'50 знаков')
    social_card = models.ImageField(
        verbose_name=u'Карточка для социальных сетей', upload_to=social_card_upload_to, blank=True, null=True
    )

    class Meta:
        abstract = True

    def get_social_label(self):
        """Получить метку для социальной карточки"""

        return self.social_label


class Category(models.Model):
    """Категории новостей и эксперта"""

    is_custom = models.BooleanField(u'Специальная категория', default=False)
    title = models.CharField(u'Название', max_length=255, blank=True)
    slug = models.SlugField(u'Алиас')
    image = ImageRemovableField(upload_to=category_image_upload_to, verbose_name=u'Изображение', blank=True, null=True)

    class Meta:
        db_table = u'news_categories'
        verbose_name = u'рубрика'
        verbose_name_plural = u'рубрики'

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'news:news_type', (), {'slug': self.slug}

    @models.permalink
    def get_expert_url(self):
        """Ссылка на пресс-конференции этой категории"""

        return 'experts.views.category', (), {'category_alias': self.slug}


class Subject(SocialCardMixin, models.Model):
    """Сюжеты (темы)"""

    title = models.CharField(u'название', max_length=255)
    caption_small = models.TextField(u'краткое описание')
    caption = models.TextField(u'описание')
    slug = models.SlugField(u'алиас', db_index=True)
    is_visible = models.BooleanField(u'Показывать', default=True, db_index=True)
    background_image = ImageRemovableField(
        upload_to='img/site/news/subject', blank=True, null=True, verbose_name=u'фоновое изображение',
        help_text=u'Размер изображения: 1920x250') # min_size=(1920, 250), max_size=(1920, 250)
    show_on_home = models.BooleanField(
        u'Показывать на главной', default=False, db_index=True,
        help_text=u'Сюжет должен содержать минимум 2 материала и 3 новости')
    home_image = ImageRemovableField(
        upload_to='img/site/news/subject', blank=True, null=True, verbose_name=u'изображение для главной',
        help_text=u'Размер изображения: 1920x400') # min_size=(1920, 400), max_size=(1920, 400)

    class Meta:
        db_table = u'news_subjects'
        verbose_name = u'сюжет'
        verbose_name_plural = u'сюжеты'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('news:subjects:read', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.show_on_home:
            # Сюжет на главной может быть только один
            Subject.objects.filter(show_on_home=True).update(show_on_home=True)

        return super(Subject, self).save(*args, **kwargs)

    def get_social_label(self):
        """Получить метку для социальной карточки"""

        return super(Subject, self).get_social_label() or u'Сюжет'


@material_register_signals
class BaseMaterial(CommentMixin, SocialCardMixin, PostmetaMixin, models.Model):
    """Базовый класс для всех материалов: новости, статьи, фоторепортажи, видео, инфографика

    Если в отдельном разделе нужны свои дополнительные поля для материала,
    необходимо наследовать модель раздела от любого материала здесь.
    """

    stamp = models.DateField(u'Дата', db_index=True)
    published_time = models.TimeField(u'Время публикации', null=True, blank=True, db_index=True)

    subject = models.ForeignKey(Subject, null=True, blank=True, verbose_name=u'Сюжет', related_name='news_%(class)s')
    subject_main = models.BooleanField(u'главное в сюжете', default=False, blank=True, db_index=True)

    category = models.ForeignKey(
        Category, null=True, blank=True, verbose_name=u'Рубрика', related_name='news_%(class)s'
    )

    project = models.ForeignKey(
        Project, null=True, blank=True, verbose_name=u'Спецпроект', related_name='news_materials', default=None
    )

    title = models.CharField(u'Заголовок', max_length=765)
    slug = models.SlugField(u'Алиас')
    author = models.CharField(u'Автор', blank=True, max_length=2000)
    caption = models.TextField(u'Подводка', blank=True)
    content = models.TextField(u'Содержание', blank=True)

    is_hidden = models.BooleanField(u'Скрытая', db_index=True, default=True)
    # Используется для отделения наших материалов от проплаченных в Ленте новостей
    is_advertising = models.BooleanField(u'Рекламная', default=False, db_index=True)
    is_important = models.BooleanField(u'Главное', default=False, db_index=True,
                                       help_text=u'Отображать в блоке «Главное» на индексе новостей')
    is_super = models.BooleanField(u'Супер-материал', default=False, db_index=True,
                                   help_text=u'Может быть только один супер-материал.')

    created = models.DateTimeField(editable=False, auto_now_add=True, db_index=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    comments_cnt = models.PositiveIntegerField(u'Комментариев', default=0, editable=False)

    source_site = models.ForeignKey(Site, verbose_name=u'Основной раздел', null=True, blank=True)
    sites = models.ManyToManyField(Site, related_name='news_%(class)s', verbose_name=u'Разделы')

    home_position = models.BigIntegerField(
        u'Сортировка на главной странице', db_index=True, editable=False, default=big_int_from_time
    )
    stick_position = models.PositiveSmallIntegerField(u'Позиция закрепления', null=True, blank=True, db_index=True)
    stick_date = models.DateTimeField(u'Дата последнего закрепления', null=True, blank=True, db_index=True)

    gallery = ManyToGallerysField(
        help_text=u'Оптимальный размер 705х407. Минимальный 460х307. Пропорция 3:2', related_query_name='news_%(class)s'
    )

    serialized_sites = models.CharField(u'Сериализованный список идентификаторов разделов', blank=True, max_length=255)
    views_cnt = models.PositiveIntegerField(u'Просмотры', db_index=True, editable=False, default=0)
    popularity = models.PositiveIntegerField(u'Популярность', db_index=True, editable=False, default=0)

    # Число дня
    is_number_of_day = models.BooleanField(u'Отображать как "Число дня"', default=False)
    number_of_day_number = models.CharField(u'Число', max_length=250, blank=True, default='')
    number_of_day_text = models.TextField(u'Текст', blank=True, default='')

    # Журнал
    magazine = models.ForeignKey(
        'magazine.Magazine', verbose_name=u'Журнал', null=True, blank=True, related_name='news_magazine_materials'
    )
    magazine_author = models.ForeignKey(
        'magazine.MagazineAuthor', verbose_name=u'Автор материала в журнале', null=True, blank=True
    )
    magazine_position = models.IntegerField(u'Позиция в журнале', db_index=True, default=0, blank=True)
    magazine_image = models.ImageField(
        upload_to='img/site/news/magazine', blank=True, null=True, verbose_name=u'Фото для журнала'
    )

    # content_type материала
    content_type = models.ForeignKey(ContentType, editable=False, verbose_name=u'тип материала', null=True, blank=True)
    # content_object возвращает объект фактического типа материала.
    content_object = GenericForeignKey('content_type', 'id')

    # Количество кликов на соц. кнопки
    vk_share_cnt = models.PositiveIntegerField(u'Вконтакте', default=0)
    tw_share_cnt = models.PositiveIntegerField(u'Твиттер', default=0)
    ok_share_cnt = models.PositiveIntegerField(u'Одноклассники', default=0)
    fb_share_cnt = models.PositiveIntegerField(u'Facebook', default=0)

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    tags = TaggableManager(blank=True)

    class Meta:
        db_table = 'news_basematerial'
        verbose_name = u'материал'
        verbose_name_plural = u'материалы'
        index_together = [('stamp', 'published_time')]
        permissions = (('can_see_hidden', 'Can see hidden materials'),)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        """Получить абсолютный url для материала"""

        if self.is_specific():
            handler = self
        else:
            handler = self.content_type.model_class()

        return (
            handler.get_magazine_url(self) or
            handler.get_material_url(self)
        )

    def get_absolute_url_with_domain(self):
        """
        Получить абсолютный урл с доменом

        Ex.: https://www.irk.ru/news/article/1/
        """

        return '{schema}{domain}{path}'.format(
            schema=settings.SITE_SCHEMA,
            domain=CurrentSite.get_site_url('www', False),
            path=self.get_absolute_url(),
        )

    @staticmethod
    def get_material_url(material):
        """Статический метод для получения url материала. Перегружается в потомках, когда это необходимо"""

        kwargs = {
            'year': material.stamp.year,
            'month': '%02d' % material.stamp.month,
            'day': '%02d' % material.stamp.day,
            'slug': material.slug,
        }
        try:
            return reverse('{0.app_label}:{0.model}:read'.format(material.content_type), kwargs=kwargs)
        except NoReverseMatch:
            return reverse('news:{}:read'.format(material.content_type.model), kwargs=kwargs)

    @staticmethod
    def get_magazine_url(material):
        """Если материал относится к журналу, то возвращает соответствующий url"""

        if hasattr(material, 'magazine') and material.magazine:
            try:
                return reverse(
                    'magazine:router', kwargs={'magazine_slug': material.magazine.slug, 'material_id': material.pk}
                )
            except NoReverseMatch:
                pass

    def get_admin_url(self):
        """Получить ссылку для редактирования материала в админке"""

        return reverse_lazy(admin_urlname(self.content_object._meta, 'change'), args=[self.pk])

    def title_with_type(self):
        """Заголовок с типом материала"""

        return u'{} ({})'.format(self.title, self._meta.verbose_name.title())

    def get_sorting_key(self):
        """
        Получить ключ сортировки.
        Используется, когда нужно сортировать материалы разных видов.
        """
        if self.published_time is None:
            return datetime.datetime.combine(self.stamp, datetime.time(0))
        else:
            return datetime.datetime.combine(self.stamp, self.published_time)

    def is_specific(self):
        """Проверить, является ли объект экземпляром конкрентной модели, а не базовой"""

        if self.pk:
            return self.content_type_id == ContentType.objects.get_for_model(self, for_concrete_model=False).id
        else:
            return self.__class__ is not BaseMaterial

    def cast(self):
        """Если объект представлен базовым классом, возвращает объект фактического типа"""

        if not self.is_specific():
            return self.content_object

        return self

    def uncast(self):
        """Если объект фактического типа, вернуть объект базового класса"""

        if self.is_specific():
            return BaseMaterial.objects.get(pk=self.pk)

        return self

    def is_sticked(self):
        """Закрепленный материал"""

        return self.stick_position is not None

    def set_stick_position(self, position, save=False):
        """
        Закрепить материал на определенной позиции
        :param position: позиция на которой закрепляется материал
        :type position: int or None
        :param bool save: если True, то экземпляр модели сохраняется в БД. Default: False
        """

        position = int_or_none(position)

        if self.stick_position != position:
            self.stick_position = position
            self.stick_date = datetime.datetime.now()
            if save:
                self.save()

    def save(self, *args, **kwargs):

        if not self.pk:
            self.content_type = ContentType.objects.get_for_model(self, for_concrete_model=False)

        # Супер-материал может быть только один
        if self.is_super:
            BaseMaterial.objects.filter(is_super=True).update(is_super=False)

        super(BaseMaterial, self).save(*args, **kwargs)

        if not settings.TESTS_IN_PROGRESS:
            # добавим материал на индекс статей
            from irk.news.controllers import ArticleIndexController  # цикличный импорт
            controller = ArticleIndexController()
            controller.material_updated(self)

    @property
    def wide_image(self):
        """Широкоформатное изображение материала"""

        if hasattr(self, 'image'):
            return self.image
        else:
            return None

    @property
    def standard_image(self):
        """Стандартное изображение материала"""

        picture = self.gallery.main_image()
        if picture:
            return picture.image

    @property
    def label(self):
        """Текстовая метка для объекта"""

        return self._meta.verbose_name.capitalize()

    def get_social_label(self):
        """Получить метку для карточки социальных сетей"""

        return super(BaseMaterial, self).get_social_label() or (self.project.title if self.project else u'')

    def is_longread(self):
        """Материал является лонгридом"""

        return self.content_type.model != 'news'

    @property
    def published_datetime(self):
        """Дата публикации в виде datetime"""
        if self.stamp:
            if self.published_time:
                return datetime.datetime.combine(self.stamp, self.published_time)
            else:
                return datetime.datetime.combine(self.stamp, datetime.time())


@material_register_signals
class News(BaseMaterial):
    """Новость"""
    is_main = models.BooleanField(u'Главная', default=False, db_index=True)  # Не используется
    is_payed = models.BooleanField(u'Платная', default=False, db_index=True)
    is_exported = models.BooleanField(u'Выводится в Яндекс.новостях', default=True, db_index=True)
    is_auto_disable_comments = models.BooleanField(u'Отключать комменарии автоматически', default=True, db_index=True)
    hide_main_image = models.BooleanField(u'Отключить главную картинку', default=False, db_index=True)
    has_video = models.BooleanField(u'Есть видео', default=False, db_index=True)
    has_audio = models.BooleanField(u'Есть аудио', default=False, db_index=True)
    city = models.ForeignKey('map.Cities', verbose_name=u'Город', null=True, blank=True)
    bunch = models.ForeignKey('self', null=True, blank=True, default=None, verbose_name=u'Предыдущая связанная новость',
                              related_name='news_bunch')
    image = ImageRemovableField(verbose_name=u'Большая фотография', blank=True, upload_to=wide_image_upload_to)

    # Официальный комментарий для rss яндекса
    official_comment_text = models.CharField(u'Текст', max_length=300, blank=True, default='')
    official_comment_name = models.CharField(u'Автор', max_length=300, blank=True, default='')
    official_comment_link = models.URLField(u'Ссылка на первоисточник', max_length=300, blank=True, default='')
    official_comment_logo = models.ImageField(verbose_name=u'Логотип компании источника цитаты или фото автора',
                            upload_to='img/site/news/official_comment_logo/',
                            help_text=u'Размер от: 128х128 px', blank=True)
    official_comment_bind = models.URLField(u'Ссылка на опровергаемую новость', max_length=300, blank=True, default='')

    # Видео для rss яндекса
    rss_video_preview = models.ImageField(verbose_name=u'Превью для видео',
                        upload_to='img/site/news/video_preview/',
                        null=True, default=None, blank=True)
    rss_video_link = models.URLField(u'Ссылка видео', max_length=300, blank=True, default='')

    search = search.NewsSearch()

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    class Meta:
        db_table = 'news_news'
        verbose_name = u'новость'
        verbose_name_plural = u'новости'

    @property
    def wide_image(self):
        # У Новостей нет широкоформатной фотографии

        return None

    @staticmethod
    def get_material_url(material):
        # Обработка новостей с bb кодом [url] в заголовке
        if '[/url]' in material.title:
            m = re.search(r'\[url\s(.*?)\]', material.title)
            if m:
                return m.group(1)

        return BaseMaterial.get_material_url(material)

    def get_social_label(self):
        """Получить метку для карточки социальных сетей"""

        return super(News, self).get_social_label() or u'Новости'


@material_register_signals
class Photo(BaseMaterial):
    """Фоторепортаж"""

    caption_short = models.TextField(u'Сокращенная подводка (для фотографии)', blank=True, max_length=290,
                                     help_text=u'Не больше 290 символов')
    image = models.ImageField(verbose_name=u'Широкоформатная фотография', upload_to=wide_image_upload_to,
                              help_text=u'Размер: 1180х560 пикселей', blank=True)
    was_paid = models.BooleanField(u'Платный материал', default=False, db_index=True,
                                   help_text=u'Используется для статистики')
    share_text = models.CharField(u'Подпись для социокнопок', max_length=255, blank=True)

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    search = search.PhotoSearch()

    class Meta:
        db_table = 'news_photo'
        verbose_name = u'фоторепортаж'
        verbose_name_plural = u'фоторепортажи'

    def get_social_label(self):
        return super(Photo, self).get_social_label() or u'Фоторепортажи'


class TemplateMixin(models.Model):
    """
    Этот миксин позволяет выбирать шаблона для материала
    """
    TEMPLATE_NOT_SET = 0
    TEMPLATE_IMAGE_HEADER = 1
    TEMPLATE_ITALIC_HEADER = 2
    TEMPLATE_CHOICES = (
        (TEMPLATE_NOT_SET, 'по умолчанию'),
        (TEMPLATE_ITALIC_HEADER, 'курсивный заголовок'),
        (TEMPLATE_IMAGE_HEADER, 'с фоновой фотографией'),
    )

    template = models.PositiveIntegerField(u'Шапка статьи', choices=TEMPLATE_CHOICES, default=0)
    header_image = models.ImageField(
        verbose_name=u'Фоновая фотография шапки', upload_to=wide_image_upload_to,
        help_text=u'Размер: 1920х600 пикселей', blank=True
    )

    class Meta:
        abstract = True

    def is_italic_header(self):
        return self.template == self.TEMPLATE_ITALIC_HEADER

    def is_image_header(self):
        return self.template == self.TEMPLATE_IMAGE_HEADER


@material_register_signals
class Article(TemplateMixin, BaseMaterial):
    """Статья"""

    type = models.ForeignKey('ArticleType', verbose_name=u'Тип', related_name='articles')
    image = models.ImageField(
        verbose_name=u'Широкоформатная фотография', upload_to=wide_image_upload_to,
        help_text=u'Размер: 1180х560 пикселей', blank=True
    )
    image_label = models.CharField(u'Подпись для фотографии', max_length=255, blank=True)
    is_paid = models.BooleanField(u'Платная', default=False, db_index=True)
    # TODO: Удалить после релиза Бигфута
    was_paid = models.BooleanField(u'Платный материал', default=False, db_index=True,
                                   help_text=u'Используется для статистики')
    paid = models.DateTimeField(u'Время установки платной', editable=False, null=True, blank=True, db_index=True)
    introduction = models.CharField(u'Введение', max_length=1000, blank=True)

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    search = search.ArticleSearch()

    class Meta:
        db_table = 'news_article'
        verbose_name = u'статья'
        verbose_name_plural = u'статьи'

    def fill_introduction(self, save=True):
        """
        Заполнить поле «Введение» для статьи

        :param bool save: Если True, то модель сохранятеся в БД.
        """

        if not self.content:
            return

        match = re.search(ur'\[intro\](.*)\[/intro\]', self.content, re.S)
        if match:
            self.introduction = match.group(1)
            if save:
                self.save()

    def get_social_label(self):
        """Получить метку для карточки социальных сетей"""

        return super(Article, self).get_social_label() or self.type.social_label if self.type else u''


@material_register_signals
class Video(BaseMaterial):
    """Видео"""

    preview = ImageRemovableField(verbose_name=u'Превью', upload_to='img/site/news/video',
                    help_text=u'Размер: 800x378 пикселей') #  max_size=(800, 378), min_size=(800, 378),

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    search = search.VideoSearch()

    class Meta:
        db_table = 'news_video'
        verbose_name = u'видео'
        verbose_name_plural = u'видео'

    @property
    def wide_image(self):
        # У видео это поле preview

        if hasattr(self, 'preview'):
            return self.preview
        else:
            return None

    def get_social_label(self):
        return super(Video, self).get_social_label() or u'Видео'


@material_register_signals
class Infographic(BaseMaterial):
    image = ImageRemovableField(verbose_name=u'Инфографика', upload_to='img/site/news/infographic',
                             help_text=u'Размер: 960×&infin; пикселей')  # max_size=(960, 1000000),
    preview = ImageRemovableField(verbose_name=u'Превью', upload_to='img/site/news/infographic',
                               help_text=u'Размер: 940x445 пикселей')  # max_size=(940, 445),  min_size=(940, 445)
    thumbnail = ImageRemovableField(verbose_name=u'Миниатюра', upload_to='img/site/news/infographic',
                                 help_text=u'Размер: 300×200 пикселей')  # min_size=(300, 200), max_size=(300, 200),
    iframe_url = models.CharField(u'Адрес iframe', blank=True, max_length=100)
    iframe_height = models.PositiveIntegerField(default=600)

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    search = search.InfographicSearch()

    @staticmethod
    def get_material_url(material):
        name = '{}:{}:read'.format(material.source_site.slugs, material.content_type.model)
        return reverse_lazy(name, args=(material.pk,))

    class Meta:
        db_table = 'news_infographics'
        verbose_name = u'инфографика'
        verbose_name_plural = u'инфографика'

    def __unicode__(self):
        return self.title

    @property
    def wide_image(self):
        # У инфографики это поле preview

        if hasattr(self, 'preview'):
            return self.preview
        else:
            return None

    @property
    def standard_image(self):
        # У инфографики это поле совпадает с wide_image

        return self.wide_image

    def get_social_label(self):
        return super(Infographic, self).get_social_label() or u'Инфографика'


@material_register_signals
class Metamaterial(BaseMaterial):
    """
    Новостной метаматериал

    Метаматериал - это материал, который в списке выглядит как настоящий
    (с картинкой и заголовком), но по сути является простой ссылкой
    на произвольный URL.
    """

    url = models.URLField(u'ссылка')
    image = models.ImageField(
        verbose_name=u'Широкоформатная фотография', upload_to=wide_image_upload_to,
        help_text=u'Размер: 1180х560 пикселей', blank=True
    )
    image_3x2 = models.ImageField(
        verbose_name=u'Стандартная фотография', upload_to=wide_image_upload_to,
        help_text=u'Размер: 705х470. Пропорция 3:2', blank=True
    )

    is_special = models.BooleanField(u'Спецпроект', default=False, db_index=True)
    show_on_home = models.BooleanField(u'Показывать в блоке Спецпроектов на главной', default=False, db_index=True)

    class Meta:
        verbose_name = u'метаматериал'
        verbose_name_plural = u'метаматериалы'

    @staticmethod
    def get_material_url(material):
        material = material.cast()
        return material.url

    @property
    def standard_image(self):
        return self.image_3x2


@material_register_signals
class Podcast(BaseMaterial):
    """Подкасты"""

    link = models.URLField(u'ссылка')
    _wide_image = models.ImageField(
        verbose_name=u'Широкоформатная фотография', upload_to=wide_image_upload_to,
        help_text=u'Размер: 940х445 пикселей', blank=True
    )
    _standard_image = models.ImageField(
        verbose_name=u'Стандартная фотография', upload_to=wide_image_upload_to,
        help_text=u'Размер: 705х470. Пропорция 3:2', blank=True
    )
    number = models.PositiveSmallIntegerField(u'Номер подкаста', editable=False, null=True)
    introduction = models.CharField(u'Введение', max_length=1000, blank=True)

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    search = search.PodcastSearch()

    class Meta:
        verbose_name = u'подкаст'
        verbose_name_plural = u'подкасты'

    def save(self, *args, **kwargs):
        if not self.pk:
            self._save_image(self._wide_image, 'wide', find(app_settings.PODCAST_WIDE_IMAGE))
            self._save_image(self._standard_image, 'standard', find(app_settings.PODCAST_STANDARD_IMAGE))
            self.number = (Podcast.objects.aggregate(Max('number'))['number__max'] or 0) + 1

        return super(Podcast, self).save(*args, **kwargs)

    def _save_image(self, field, name, path):
        """
        Save file into field
        """

        with open(path, 'rb') as f:
            field.save(name, File(f), save=False)

    @property
    def wide_image(self):
        return self._wide_image

    @property
    def standard_image(self):
        return self._standard_image

    def is_longread(self):
        return False

    def get_social_label(self):
        return super(Podcast, self).get_social_label() or u'Подкаст'

    def fill_introduction(self, save=True):
        """
        Заполнить поле «Введение» для подкаста

        :param bool save: Если True, то модель сохранятеся в БД.
        """

        if not self.content:
            return

        match = re.search(ur'\[intro\](.*)\[/intro\]', self.content, re.S)
        if match:
            self.introduction = match.group(1)
            if save:
                self.save()


class ArticleType(models.Model):
    """Тип статьи"""

    title = models.CharField(u'Название', max_length=255)
    social_label = models.CharField(u'Метка для социокарточки', max_length=255, blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = 'news_article_types'
        verbose_name = u'Тип статей'
        verbose_name_plural = u'Типы статей'

    def save(self, *args, **kwargs):
        # По умолчанию метка совпадает с названием.
        if not self.social_label:
            self.social_label = self.title

        super(ArticleType, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title


class Flash(CommentMixin, models.Model):
    """Народные новости"""

    # Источники новостей
    TWITTER = 1
    SMS = 2
    SITE = 3
    VK_DTP = 4
    TYPES = (
        (TWITTER, u'Twitter'),
        (SMS, u'SMS'),
        (SITE, u'Сайт'),
        (VK_DTP, u'Вконтакте ДТП'),
    )

    instance_id = models.CharField(u'Идентификатор', blank=True, max_length=20)
    type = models.PositiveIntegerField(u'Тип новости', choices=TYPES)
    author = models.ForeignKey(User, null=True, blank=True)
    username = models.CharField(u'Автор', max_length=15, blank=True)  # Twitter username или номер мобильного телефона
    title = models.CharField(u'Заголовок', max_length=255, blank=True)
    content = models.TextField(u'Текст', blank=True)
    visible = models.BooleanField(u'Показывать', default=True, db_index=True)
    created = models.DateTimeField(u'Дата создания', default=datetime.datetime.now)
    comments_cnt = models.PositiveIntegerField(u'Комментариев', default=0, editable=False)
    video_thumbnail = ImageRemovableField(verbose_name=u'Превью видео', upload_to='img/site/news/flash', blank=True, null=True)

    gallery = ManyToGallerysField()

    class Meta:
        db_table = u'news_flash'
        verbose_name = u'народная новость'
        verbose_name_plural = u'народные новости'

    def __unicode__(self):
        return self.title or self.content

    @models.permalink
    def get_absolute_url(self):
        return 'news:flash:read', (self.pk,), {}

    @property
    def is_tweet(self):
        return self.type == Flash.TWITTER

    @property
    def is_sms(self):
        return self.type == Flash.SMS

    @property
    def is_site(self):
        return self.type == Flash.SITE

    @property
    def is_vk_dtp(self):
        return self.type == Flash.VK_DTP


class FlashBlock(models.Model):
    """Блокировка авторов народных новостей"""

    pattern = models.CharField(u'Имя пользователя', max_length=50)

    class Meta:
        db_table = u'news_flash_block'
        verbose_name = u'бан по номеру телефона или twitter'
        verbose_name_plural = u'бан по номеру телефона или twitter'

    def __unicode__(self):
        return self.pattern


class Subscriber(models.Model):
    """Подписчик на рассылку новостей"""

    email = models.EmailField(u'E-mail', max_length=40, primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True)
    hash = models.CharField(max_length=40, editable=False)
    is_active = models.BooleanField(u'Активирован', default=True, db_index=True)
    hash_stamp = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now, editable=False)

    class Meta:
        db_table = 'news_distribution_subscribers'
        verbose_name = u'подписчик'
        verbose_name_plural = u'подписчики'

    def __unicode__(self):
        return self.email

    def generate_hash(self):
        """Создает временный хеш для подтверждения регистрации, либо для восстановления пароля."""

        if not self.hash:
            self.hash = get_hexdigest('sha1', str(random.random()), str(random.random()))
        self.hash_stamp = datetime.datetime.now()
        self.save()


class BaseNewsletter(models.Model):
    """
    Базовый класс для рассылок материалов.
    """

    # текстовая метка рассылки
    label = None
    # Заголовок рассылки
    title = None

    STATUS_NEW = 1
    STATUS_SENT = 2
    STATUS_FAIL = 3
    STATUS_CHOICES = (
        (STATUS_NEW, u'новая'),
        (STATUS_SENT, u'отправлена'),
        (STATUS_FAIL, u'не отправлена'),
    )

    status = models.PositiveSmallIntegerField(u'состояние', choices=STATUS_CHOICES, default=STATUS_NEW)
    created = models.DateTimeField(u'создана', auto_now_add=True)
    sent = models.DateTimeField(u'завершена', null=True)
    sent_cnt = models.PositiveIntegerField(u'подписчики', default=0, editable=False)
    views_cnt = models.PositiveIntegerField(u'просмотры', default=0, editable=False)

    materials = models.ManyToManyField(BaseMaterial, related_name='+', through='MaterialNewsletterRelation')

    objects = BaseNewsletterManager()

    class Meta:
        verbose_name = u'новостная рассылка'
        verbose_name_plural = u'новостные рассылки'

    def is_sent(self):
        """Отправлена ли рассылка?"""

        return self.status == self.STATUS_SENT

    def has_materials(self):
        """Имеются ли материалы?"""

        return self.materials.exists()

    def add(self, material):
        """Добавить материал в рассылку"""

        if not self.materials.filter(pk=material.id).exists():
            MaterialNewsletterRelation.objects.create(material=material, newsletter=self)

    def remove(self, material):
        """Удалить материал из рассылки"""

        MaterialNewsletterRelation.objects.filter(material=material, newsletter=self).delete()

    def clear(self):
        """Удалить все материалы из рассылки"""

        self.materials.clear()

    def set(self, materials):
        """
        Поставить список материалов в рассылку.
        Все ранее имеющиеся в рассылке материалы удаляются.
        """

        self.clear()

        for material in materials:
            self.add(material)

    def update_status(self, count=None):
        """
        Обновить статус рассылки.

        Если count равно None или 0, то присваивается статус "не отправлена".
        Иначе присваивается статус "отправлена" и сохраняется количество отправленных писем и время окончания отправки.
        """

        if count:
            self.status = self.STATUS_SENT
            self.sent_cnt = count
            self.sent = datetime.datetime.now()
        else:
            self.status = self.STATUS_FAIL

        self.save()

    @classmethod
    def get_current(cls):
        """Получить текущую актуальную рассылку"""

        # реализация в подклассах
        raise NotImplementedError()

    def get_date_label(self):
        """Получить метку даты отправки"""

        # реализация в подклассах
        raise NotImplementedError()

    @property
    def statistic_url(self):
        """URL для сбора статистики просмотров рассылки"""

        return u'/hydra/newsletter/statistic/{0.id}.png'.format(self)


class DailyNewsletter(BaseNewsletter):
    """Ежедневная рассылка материалов"""

    label = 'daily'
    title = u'Редакция IRK.ru подготовила по итогам дня подборку материалов о самых значимых и интересных событиях, ' \
            u'случившихся в Иркутске и области.'

    date = models.DateField(u'дата отправки', db_index=True)

    @classmethod
    def get_current(cls):
        today = datetime.date.today()

        instance, created = cls.objects.get_or_create(date=today)

        return instance

    def get_date_label(self):
        return u'{0.date:%d%m%Y}'.format(self)

    def __unicode__(self):
        return u'Рассылка на {0.date:%d.%m.%Y}'.format(self)

    def get_absolute_url(self):
        return reverse_lazy('news:newsletter_materials', kwargs={'period': 'daily'})


class WeeklyNewsletter(BaseNewsletter):
    """Еженедельная рассылка материалов"""

    label = 'week'
    title = u'Редакция IRK.ru подготовила по итогам недели подборку материалов о самых значимых и интересных ' \
            u'событиях, случившихся в Иркутске и области.'

    year = models.PositiveSmallIntegerField(u'год')
    week = models.PositiveSmallIntegerField(u'неделя')

    @classmethod
    def get_current(cls):
        today = datetime.date.today()
        year, week, _ = today.isocalendar()

        instance, created = cls.objects.get_or_create(year=year, week=week)

        return instance

    def __unicode__(self):
        start_date = datetime.date(self.year, 1, 1)

        # надо учесть вариант, когда последняя неделя года заканчивается уже в новом году
        end_date = datetime.date(self.year + 1, 1, 7)

        # находим понедельник и воскресенье недели
        period = rrule.rrule(
            rrule.DAILY, byweekno=self.week, dtstart=start_date, until=end_date, byweekday=[rrule.MO, rrule.SU]
        )
        return u'Рассылка на неделю c {0:%d.%m.%Y} по {1:%d.%m.%Y}'.format(*period)

    def get_date_label(self):
        return u'{0.week}{0.year}'.format(self)

    def get_absolute_url(self):
        return reverse_lazy('news:newsletter_materials', kwargs={'period': 'weekly'})


class MaterialNewsletterRelation(models.Model):
    """Связь материалов с рассылками"""

    material = models.ForeignKey(BaseMaterial, related_name='+')
    newsletter = models.ForeignKey(BaseNewsletter, related_name='material_relations')
    position = models.BigIntegerField(u'позиция', db_index=True, editable=False, default=big_int_from_time)

    class Meta:
        verbose_name = u'материал рассылки'
        verbose_name_plural = u'материалы рассылок'
        ordering = ['position']
        unique_together = ('material', 'newsletter')

    def __unicode__(self):
        return u'Материал {0.material_id} в рассылке {0.newsletter_id}'.format(self)


class Mailer(models.Model):
    """Рассылка для информационных агенств """

    mails = models.TextField(u'Список адресов', help_text=u'Список email через запятую')
    title = models.CharField(u'Тема письма', max_length=255, blank=True, null=True)
    file = FileRemovableField(verbose_name=u'Файл', upload_to='img/site/news/mailer_files', blank=True, null=True)
    text = models.TextField(u'Текст', blank=True, null=True)
    stamp = models.DateTimeField(u'Дата рассылки', auto_now_add=True)

    class Meta:
        verbose_name = u'рассылка для информационных агенств'
        verbose_name_plural = u'рассылки для информационных агенств'

    def __unicode__(self):
        return '%s %s' % (self.stamp, self.title)


class UrgentNews(models.Model):
    """Новость-молния"""

    text = models.CharField(u'Текст', max_length=255)
    is_visible = models.BooleanField(u'Показывать', default=False)
    created = models.DateTimeField(u'Дата создания')

    class Meta:
        db_table = 'news_urgent'
        verbose_name = u'срочная новость'
        verbose_name_plural = u'срочные новости'

    def __unicode__(self):
        return self.text


class Live(models.Model):
    """Онлайн-трансляция событий"""

    news = models.ForeignKey(News)
    is_finished = models.BooleanField(u'Завершена', default=False)

    class Meta:
        db_table = u'news_live'
        verbose_name = u'онлайн-трансляция'
        verbose_name_plural = u'онлайн-трансляции'

    def __unicode__(self):
        return unicode(self.news)

    def get_absolute_url(self):
        return self.news.get_absolute_url()

    def save(self, *args, **kwargs):
        cache.delete('news.live.%s' % self.pk)
        super(Live, self).save(*args, **kwargs)


def default_now_time():
    return datetime.datetime.now().time()


class LiveEntry(models.Model):
    """Событие онлайн-трансляции"""

    live = models.ForeignKey(Live, related_name='entries')
    text = models.TextField(u'Текст', blank=True, null=True)
    is_important = models.BooleanField(u'Важное', default=False)
    created = models.TimeField(u'Время', default=default_now_time, blank=True)
    date = models.DateField(u'Дата', default=datetime.date.today)
    image = ImageRemovableField(verbose_name=u'Картинка', upload_to='img/site/news/live', blank=True, null=True)

    class Meta:
        db_table = u'news_live_entries'

    def __unicode__(self):
        return self.text

    def save(self, *args, **kwargs):
        cache.delete('news.live.%s' % self.live_id)
        super(LiveEntry, self).save(*args, **kwargs)


class Block(models.Model):
    """
    Блок материалов на странице.
    Содержит определенное количество материалов. Материалы привязаны к конкретной позиции.
    """

    name = models.CharField(u'Название', max_length=100)
    slug = models.CharField(u'Алиас', max_length=50, db_index=True)
    position_count = models.PositiveSmallIntegerField(u'Количество позиций', default=0)

    class Meta:
        verbose_name = u'Блок материалов'
        verbose_name_plural = u'Блоки материалов'

    def __unicode__(self):
        return self.name


class Position(models.Model):
    """
    Позиция материала в блоке.
    """

    block = models.ForeignKey(Block, related_name='positions')
    number = models.PositiveSmallIntegerField(u'Номер позиции')
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.IntegerField(null=True)
    material = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['number', ]
        verbose_name = u'Позиция'
        verbose_name_plural = u'Позиции'

    def __unicode__(self):
        chunks = [u'Позиция: {}'.format(self.number)]
        if self.object_id:
            chunks.append(u'Материал: {}'.format(self.material))
        return u' '.join(chunks)


class Quote(models.Model):
    text = models.TextField(u'Текст', blank=True, null=True)
    title = models.CharField(u'Заголовок', max_length=250)
    is_hidden = models.BooleanField(u'Скрытая', default=False)
    created = models.DateTimeField(editable=False, auto_now_add=True, db_index=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = u'цитата'
        verbose_name_plural = u'цитаты'

    def __unicode__(self):
        return self.title


class ScheduledTask(models.Model):
    """
    Запланированная задача публикации материала

    Например, завтра в 15:00 опубликовать новость.

    Только одну такую задачу можно создать для любого BaseMaterial. Логику
    создания/удаления задач реализует админский миксин SchedulerAdminMixin.

    Пока единственный тип задачи - publish
    """
    STATE_SCHEDULED = 'scheduled'
    STATE_DONE = 'done'
    STATE_CANCELED = 'canceled'
    STATE_CHOICES = (
        (STATE_SCHEDULED, u'Запланирована'),
        (STATE_DONE, u'Успешно завершена'),
        (STATE_CANCELED, u'Была запланирована, но отменилась'),
    )

    TASK_PUBLISH = 'publish'

    material = models.OneToOneField(BaseMaterial, related_name='scheduled_task')
    when = models.DateTimeField(u'Должна запуститься')
    updated = models.DateTimeField(u'Последнее обновление', auto_now=True)
    task = models.CharField(u'Задача', max_length=250, default=TASK_PUBLISH)
    state = models.CharField(u'Статус', max_length=50, default=STATE_SCHEDULED, choices=STATE_CHOICES)
    log = models.TextField(u'Лог выполнения', blank=True, default='')

    class Meta:
        verbose_name = u'Запланированная публикация'
        verbose_name_plural = u'Запланированные публикации'

    def __unicode__(self):
        return self.material.title

    @classmethod
    def get_due_tasks(cls, now):
        """
        Возвращает инстансы задач, время выполнения которых пришло
        """
        return cls.objects.filter(when__lte=now, state=cls.STATE_SCHEDULED)

    @property
    def is_scheduled(self):
        return self.state == self.STATE_SCHEDULED

    @property
    def is_done(self):
        return self.state == self.STATE_DONE

    def logmsg(self, msg):
        """
        Добавить информацию в поле log объекта
        """
        now = datetime.datetime.now()
        self.log += u'{0:%x %X} {1}\n'.format(now, msg)
        self.log = self.log.lstrip()

        logger.debug(msg)  # чтобы в селери логировать

    def run(self):
        """
        Выполнить запланированную задачу
        Пока умеет только публиковать какой-то материал
        """
        self.logmsg(u'Выполнение задачи {}'.format(self.task))
        if self.task == self.TASK_PUBLISH:
            logger.debug(' Publishing material id=%d', self.material.id)

            # на модель материала навешан invalidate cache - поэтому нужен cast()
            material = self.material.cast()
            material.is_hidden = False
            material.save()
            logger.debug(' Material saved')

            self.state = self.STATE_DONE
            self.save()


class SocialPultDraft(models.Model):
    """
    Хранит сериализованную строку с данными черновика для поста в соц. пульте
    """
    material = models.OneToOneField(BaseMaterial, primary_key=True, related_name='social_pult_draft', on_delete=models.CASCADE)
    data = models.TextField(u'Данные редактора', blank=True, default='')


class SocialPultPost(models.Model):
    """
    Пост в соцсети как единица, с которой работает редактор - с заполненным
    текстом, отмеченными галочками.

    Основная цель этого класса - объединить SocialPost в группу. Редактор
    написала текст, отправила - эта группа публикуется. Если нужно будет
    переделать пост, то создается новая группа и снова отправляется.

    Индивидуальные посты в каждую сеть отдельно отслеживаются через объекты
    SocialPost.
    """
    material = models.ForeignKey(BaseMaterial, related_name='social_pult_post', on_delete=models.CASCADE)
    text = models.CharField(u'Текст', max_length=10000, default='')
    text_twitter = models.CharField(u'Текст для твиттера', max_length=500, default='')
    url = models.CharField(u'Ссылка', max_length=500, default='')
    selected_images = models.CharField(u'Изображения (json)', max_length=1000, default='')


class SocialPultUpload(models.Model):
    """
    Загруженное изображение для публикации в соцсети
    """
    material = models.ForeignKey(BaseMaterial, related_name='social_pult_uploads', on_delete=models.SET_NULL, null=True)
    image = FileRemovableField(u'Изображение или видео', upload_to=social_pult_upload_to,
                               validators=[FileExtensionValidator(allowed_extensions=MEDIA_EXTENSIONS)])
    created = models.DateTimeField(u'Создано', auto_now_add=True, null=True)

    @property
    def media_type(self):
        """Возвращает 'image' или 'video' для этого аплоада"""
        IMAGE = ('gif', 'jpg', 'jpeg', 'png', 'bmp', 'tif')
        VIDEO = ('mp4', 'avi', 'mkv', '3gp', 'mov', 'webm', 'm4v', 'mpeg')

        if self.image.name.endswith(IMAGE):
            return 'image'
        if self.image.name.endswith(VIDEO):
            return 'video'
        return 'unknown'


class SocialPost(models.Model):
    """
    Репост нашего материала в одной внешней соцсети.

    Также хранит информацию и состояние задачи выкладки этой самой публикации.

    Для некоторых наших материалов иногда нужно выложить репост в Одноклассники,
    или другую соцсеть. Эта модель хранит ссылку на такую публикацию, если она
    была сделана. Чтобы можно было ее удалить или отредактировать.

    Пост может быть привязан объекту SocialPultPost.
    """

    material = models.ForeignKey(BaseMaterial)
    social_pult_post = models.ForeignKey(SocialPultPost, null=True, related_name='social_posts')
    scheduled_task = models.ForeignKey(Task, null=True, on_delete=models.CASCADE)
    status = models.CharField(u'Статус публикации', default='', max_length=50)
    task_id = models.CharField(u'ID в celery', default='', max_length=100)
    network = models.CharField(u'Социальная сеть', max_length=250)
    response = models.CharField(u'Ответ соцсети (json)', max_length=2000, default='')
    error = models.CharField(u'Ошибка', max_length=2000, default='')
    link = models.CharField(u'Ссылка', max_length=250, default='')
    created = models.DateTimeField(u'Дата создания', auto_now_add=True)


class ArticleIndex(models.Model):
    """
    Таблица для сортировки индекса статей

    Работать с этой моделью лучше через контроллер, чтобы избежать проблем
    с синхронизацией.
    """

    material = models.OneToOneField(BaseMaterial, verbose_name=u'Материал', related_name='article_index',
                                   on_delete=models.CASCADE)
    position = models.BigIntegerField(u'Позиция', editable=False, default=big_int_from_time)
    admin_position = models.SmallIntegerField(u'Сортировка админом', null=True, blank=True)
    is_super = models.BooleanField(default=False, db_index=True)
    stick_position = models.PositiveSmallIntegerField(u'Позиция закрепления', null=True, blank=True, unique=True)
    stick_date = models.DateTimeField(u'Дата закрепления', null=True, blank=True)

    class Meta:
        index_together = [
            # order by position desc, admin_position desc
            ('position', 'admin_position'),
        ]

    def __unicode__(self):
        return u'ArticleIndex(id={0.id}, material_id={0.material_id}, ' \
               u'position={0.position} ({0.position_date}), ' \
               u'admin_position={0.admin_position}, is_super={0.is_super}, ' \
               u'stick_position={0.stick_position}, stick_date={0.stick_date})' \
               .format(self)

    @property
    def position_date(self):
        if self.position:
            date = datetime.datetime.fromtimestamp(self.position / 1000000)
            return date

    def is_sticked(self):
        return self.stick_position is not None

    @staticmethod
    def position_for_material(material):
        dt = material.published_datetime
        timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
        timestamp -= 8 * 60 * 60  # переведем в UTC
        return timestamp * 1000000


class TildaArticleAbstract(BaseMaterial):
    """
    Абстрактная модель для статей Тильды
    От нее наследуется статья в новостях и в обеде.
    """
    basematerial_ptr = models.OneToOneField(
        BaseMaterial, on_delete=models.CASCADE,
        parent_link=True, related_name='%(app_label)s_%(class)s_related'
    )

    tilda_content = models.TextField(u'HTML-код статьи', blank=True)
    styles = models.TextField(u'Стили', blank=True)
    scripts = models.TextField(u'Скрипты', blank=True)
    archive = FileRemovableField(u'Импорт из файла', blank=True, null=True, upload_to=tilda_upload_to)
    image = models.ImageField(
        verbose_name=u'Широкоформатная фотография', upload_to=wide_image_upload_to,
        help_text=u'Размер: 1180х560 пикселей', blank=True
    )
    image_label = models.CharField(u'Подпись для фотографии', max_length=255, blank=True)

    class Meta(BaseMaterial.Meta):
        abstract = True

    @property
    def label(self):
        # лейбл для карточек
        return u'Статья'

    def extract_path(self):
        return u'img/site/news/tilda/{year}/{folder}/'.format(
            year=self.created.year,
            folder=os.path.basename(os.path.splitext(self.archive.path)[0])
        )

    @property
    def tilda_extract_root(self):
        """Путь к папке, в которую разархивированы файлы после импорта"""
        if self.archive:
            return os.path.join(settings.MEDIA_ROOT, self.extract_path())

    @property
    def tilda_extract_url(self):
        """URL папки с распакованными файлами"""
        if self.archive:
            return settings.MEDIA_URL + self.extract_path()

    def prepare_content(self):
        """Возвращает готовый к выводу хтмл"""
        result = self.tilda_content.replace('="images/', '="{}images/'.format(self.tilda_extract_url))
        result = result.replace("='images/", "='{}images/".format(self.tilda_extract_url))
        result = result.replace('="images/', '="{}images/'.format(self.tilda_extract_url))
        result = result.replace(':"images/', ':"{}images/'.format(self.tilda_extract_url))  # джейсон в галерее зероблока
        result = result.replace('("images/js__', '("{}images/js__'.format(self.tilda_extract_url))
        result = result.replace("url('images/", "url('{}images/".format(self.tilda_extract_url))
        result = result.replace('url("images/', 'url("{}images/'.format(self.tilda_extract_url))
        return result

    def prepare_scripts(self):
        result = self.scripts.replace('src="js/', 'src="{}js/'.format(self.tilda_extract_url))
        # тильда .js файлы кладет в том числе в папку images
        result = result.replace('src="images/', 'src="{}images/'.format(self.tilda_extract_url))
        return result

    def prepare_styles(self):
        return self.styles.replace('href="css/', 'href="{}css/'.format(self.tilda_extract_url))

    def import_archive(self):
        """Распаковать и импортировать загруженный в `archive` файл из Тильды"""
        if self.archive:
            archive = IrkruTildaArchive(self.archive, material=self)
            archive.process()

    def delete_extracted(self):
        extract_dir = self.tilda_extract_root
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)


@material_register_signals
class TildaArticle(TildaArticleAbstract):

    search = search.TildaArticleSearch()

    class Meta(TildaArticleAbstract.Meta):
        verbose_name = u'статья (Тильда)'
        verbose_name_plural = u'статьи (Тильда)'

    @staticmethod
    def get_material_url(material):
        kwargs = {
            'year': material.stamp.year,
            'month': '%02d' % material.stamp.month,
            'day': '%02d' % material.stamp.day,
            'slug': material.slug,
        }
        return reverse('news:tilda_article:read', kwargs=kwargs)


# ---- Подключение сигналов ----
post_save.connect(invalidate, sender=Subject)
post_save.connect(invalidate, sender=LiveEntry)
post_save.connect(invalidate, sender=Live)
post_save.connect(invalidate, sender=Flash)
post_save.connect(invalidate, sender=Block)
post_save.connect(invalidate, sender=Position)
post_save.connect(signals.download_video_thumbnail, sender=Flash)

pre_save.connect(signals.tilda_article_pre_save, sender=TildaArticle)
post_delete.connect(signals.tilda_article_post_delete, sender=TildaArticle)
