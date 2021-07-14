# -*- coding: utf-8 -*-

import datetime
import os.path
import uuid

from dirtyfields import DirtyFieldsMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse_lazy
from django.db.models.signals import post_save

from irk.gallery.fields import ManyToGallerysField
from irk.map.models import Country
from irk.news import models as news_models
from irk.news.models import material_register_signals
from irk.phones.models import Firms as Firm, SectionFirm, Sections as Section
from irk.polls import models as polls_models
from irk.tourism import search
from irk.tourism.cache import invalidate
from irk.tourism.helpers import date_periods
from irk.tourism.management import weather
from irk.utils.fields.file import FileRemovableField, ImageRemovableField


class Place(models.Model):
    """Места отдыха"""

    # Аласы для типов мест
    TYPES_SLUG = {
        0: 'russia',
        1: 'abroad',
        2: 'baikal'
    }

    LOCAL = 0  # Россия
    EXTERNAL = 1  # Зарубеж
    BAIKAL = 2  # Байкал
    TYPES = (
        (EXTERNAL, u'Зарубеж'),
        (LOCAL, u'Россия'),
        (BAIKAL, u'Байкал'),
    )

    COUNTRY = 0
    REGION = 1
    PLACE_TYPES = (
        (COUNTRY, u'Страна'),
        (REGION, u'Регион/курорт'),
    )

    parent = models.ForeignKey('self', blank=True, null=True, related_name=u'children',
                               verbose_name=u'Родительская категория')
    country = models.ForeignKey(Country, verbose_name=u'Страна')
    title = models.CharField(u'Название', max_length=255)
    slug = models.SlugField(u'Алиас', max_length=191, unique=True)
    type = models.PositiveSmallIntegerField(u'Тип', choices=TYPES)
    short = models.TextField(u'Подводка')
    description = models.TextField(u'Описание', blank=True)
    extra_description = models.TextField(u'Дополнительное описание', blank=True,
        help_text=u'Для видео с YouTube, если в описании находятся данные от tonkosti.ru')
    content_html = models.BooleanField(u'HTML в содержании', default=False)
    position = models.PositiveSmallIntegerField(u'Позиция', blank=True)
    comments_cnt = models.PositiveIntegerField(editable=False, default=0)
    last_comment_id = models.IntegerField(null=True, editable=False)
    is_main = models.BooleanField(u'Выводить на главной', default=False, db_index=True)
    is_recommended = models.BooleanField(u'Рекомендовано', default=False, db_index=True)
    nearby = models.ManyToManyField('self', verbose_name=u'Рядом', blank=True)
    yahoo_weather_code = models.CharField(u'Код города', max_length=20, blank=True,
                                          help_text=u'Для погоды (http://weather.yahoo.com/)')
    weather_popular = models.BooleanField(u'Показывать в разделе «Погода»', default=False, db_index=True)
    tonkosti_place_type = models.PositiveIntegerField(u'Тип места', default=REGION, blank=True, choices=PLACE_TYPES)
    tonkosti_id = models.PositiveIntegerField(u'Код места на tonkosti.ru', blank=True, default=0)
    center = models.PointField(null=True, blank=True, spatial_index=False)
    promo = models.ForeignKey(Firm, null=True, blank=True, related_name='promo_place')
    flag = ImageRemovableField(upload_to='img/site/tourism/place/', null=True, blank=True, verbose_name=u'Флаг')
    # max_size=(22, 16)
    panorama_url = models.URLField(u'Адрес панорамы', blank=True,
                                   help_text=u'Только ссылка, без HTML тега &lt;iframe&gt;')
    gallery = ManyToGallerysField()

    objects = models.GeoManager()

    #Прогноз погоды на сегодня
    __forecast = None

    class Meta:
        db_table = u'tourism_places'
        verbose_name = u'место отдыха'
        verbose_name_plural = u'места отдыха'
        ordering = ['title', 'position']

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        if not self.parent:
            return 'tourism:place', (), {'place_slug': self.slug}
        else:
            return 'tourism:sub_place', (), {'parent_slug': self.parent.slug, 'place_slug': self.slug}

    def save(self, *args, **kwargs):
        if self.parent:
            self.position = self.parent.children.all().aggregate(count=models.Count('pk'))['count'] + 1
        else:
            self.position = Place.objects.filter(parent__isnull=True).aggregate(count=models.Count('pk'))['count'] + 1

        super(Place, self).save(*args, **kwargs)

    @property
    def type_slug(self):
        return dict(self.TYPES_SLUG).get(self.type)

    def get_tours(self):
        """Все туры, привязанные к гостиницам, связанным с этим местом"""

        # @todo: Cache

        return Tour.objects.filter(tourhotel__hotel__in=self.hotel_set.all(), is_hidden=False)

    tours = property(get_tours)

    def get_ways(self):
        """Как добраться до места"""

        # TODO: cache

        return Way.objects.filter(place=self).select_related()

    ways = property(get_ways)

    @property
    def forecast(self):
        """Получаем прогноз погоды по текущему месту отдыха"""

        if self.__forecast is None:
            self.__forecast = weather.load(self.pk, self.yahoo_weather_code)
        return self.__forecast

    def get_tourbases(self):
        """Турбазы"""

        return TourBase.objects.filter(place=self)


post_save.connect(invalidate, sender=Place)


def hotel_upload_to(object, filename):
    return 'img/site/tourism/hotels/%s' % filename


class Hotel(SectionFirm):
    """Гостиница"""

    place = models.ForeignKey(Place, null=True, blank=True, verbose_name=u'Место отдыха')
    price = models.CharField(u'Цена', blank=True, null=True, max_length=50)
    price_comment = models.CharField(u'Комментарий к цене', blank=True, null=True, max_length=255)
    promo = models.TextField(verbose_name=u'текст (спонсорство)', blank=True)
    level = models.PositiveSmallIntegerField(u'Количество звезд', blank=True, null=True)
    category = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'Ценовая категория')
    season = models.CharField(max_length=255, verbose_name=u'Сезон работы', blank=True, null=True)
    is_recommended = models.BooleanField(u'Рекомендовано', default=False)

    is_hotel = True  # Для определения в шаблонах

    search = search.HotelSearch()

    class Meta:
        db_table = 'tourism_hotel'
        verbose_name = u'Гостиница'
        verbose_name_plural = u'Гостиницы'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        section = Section.objects.get(content_type=ContentType.objects.get_for_model(self))

        return 'tourism:firm:read', (section.slug, self.pk), {}


class TourBase(SectionFirm):
    """Турбаза"""

    place = models.ForeignKey(Place, null=True, blank=True, verbose_name=u'Место отдыха')
    price = models.CharField(u'Цена', blank=True, null=True, max_length=50)
    price_comment = models.CharField(u'Комментарий к цене', blank=True, null=True, max_length=255)
    promo = models.TextField(verbose_name=u'текст (спонсорство)', blank=True)
    is_recommended = models.BooleanField(u'Рекомендовано', default=False)
    center = models.PointField(null=True, blank=True, spatial_index=False)
    season = models.CharField(max_length=255, verbose_name=u'Сезон работы', blank=True, null=True)

    objects = models.GeoManager()
    search = search.TourBaseSearch()

    is_tourbase = True  # Для определения в шаблонах

    class Meta:
        db_table = 'tourism_tourbases'
        verbose_name = u'турбазу'
        verbose_name_plural = u'Турбазы'

    @models.permalink
    def get_absolute_url(self):
        section = Section.objects.get(content_type=ContentType.objects.get_for_model(self))

        return 'tourism:firm:read', (section.slug, self.pk), {}


class TourFirm(SectionFirm):
    """Турфирма"""

    place = models.ForeignKey(Place, null=True, blank=True, verbose_name=u'Место отдыха')
    price = models.CharField(u'Цена', blank=True, null=True, max_length=50)
    price_comment = models.CharField(u'Комментарий к цене', blank=True, null=True, max_length=255)
    promo = models.TextField(verbose_name=u'текст (спонсорство)', blank=True)
    base = models.ForeignKey(TourBase, verbose_name=u'Турбаза', null=True, blank=True)

    search = search.TourFirmSearch()

    is_tourfirm = True  # Для определения в шаблонах

    class Meta:
        db_table = 'tourism_tourfirms'
        verbose_name = u'турфирму'
        verbose_name_plural = u'Турфирмы'

    @models.permalink
    def get_absolute_url(self):
        section = Section.objects.get(content_type=ContentType.objects.get_for_model(self))

        return 'tourism:firm:read', (section.slug, self.pk), {}


def tour_upload_to(obj, filename):
    return 'img/site/tourism/tours/%s%s' % (uuid.uuid4().hex, os.path.splitext(filename)[1])


def tour_file_upload_to(obj, filename):
    return 'img/site/tourism/tours/files/%s%s' % (uuid.uuid4().hex, os.path.splitext(filename)[1])


class Tour(DirtyFieldsMixin, models.Model):
    """Тур"""

    firm = models.ForeignKey(Firm, verbose_name=u'Фирма')
    place = models.ForeignKey(Place, blank=True, null=True, verbose_name=u'Место отдыха')
    title = models.CharField(u'Название', max_length=60, help_text=u'Не более 60 символов')
    hotels = models.ManyToManyField(to=Hotel, through='TourHotel', related_name='tours')
    short = models.CharField(u'Краткое описание', help_text=u'Выводится в результатах поиска. Не более 80 символов',
                             blank=True, max_length=80)
    description = models.TextField(u'Описание')
    price = models.PositiveIntegerField(u'Цена', db_index=True, help_text=u'Например: 42000')
    nights = models.CharField(u'Количество ночей', max_length=30, help_text=u'Например: 10 дней/11 ночей')
    is_hot = models.BooleanField(u'Горящий тур', default=False, db_index=True)
    is_recommended = models.BooleanField(u'Рекомендовано', default=False, db_index=True)
    file = FileRemovableField(upload_to=tour_file_upload_to, verbose_name=u'Описание', blank=True)
    views_cnt = models.PositiveIntegerField(default=False, editable=False)
    image = ImageRemovableField(verbose_name=u'Фото', upload_to='img/site/tourism/tour/',
                  null=True, blank=True,
                  help_text=u'Загружаемые фотографии должны быть в формате jpeg, gif, png. '
                            u'Рекомендуемый размер по ширине - 580px, по высоте - 250px.') # min_size=(580, 250), max_size=(1160, 500)
    is_hidden = models.BooleanField(u'Скрыто', default=True, db_index=True)
    gallery = ManyToGallerysField()

    class Meta:
        db_table = u'tourism_tours'
        verbose_name = u'Тур'
        verbose_name_plural = u'Туры'

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'tourism:tour:read', (), {'tour_id': self.pk}

    def get_hotels(self):
        return Hotel.objects.filter(tourhotel__tour=self.pk).all().order_by('tourhotel__position')

    def get_dates(self):
        return date_periods(TourDate.objects.filter(tour=self, date__gte=datetime.date.today()).values_list('date', flat=True).order_by('date'))

    def get_nearest_date(self):
        try:
            return TourDate.objects.filter(tour=self, date__gte=datetime.date.today()).order_by('date')[0]
        except IndexError:
            return None


class TourHotel(models.Model):
    tour = models.ForeignKey(Tour)
    hotel = models.ForeignKey(Hotel, verbose_name=u'Гостиница')
    position = models.PositiveSmallIntegerField(u'Позиция в туре', editable=False)

    class Meta:
        db_table = 'tourism_tour_hotels'
        verbose_name = u'Остановка'
        verbose_name_plural = u'Остановки'

    def save(self, *args, **kwargs):
        if not self.position:
            self.position = 0
        super(TourHotel, self).save(*args, **kwargs)


class TourDate(models.Model):
    """Времена вылетов"""

    tour = models.ForeignKey(Tour)
    date = models.DateField(u'Дата')

    class Meta:
        db_table = 'tourism_tour_periods'
        verbose_name = u'дата'
        verbose_name_plural = u'даты'

    def __unicode__(self):
        return self.date.strftime('%d.%m.%Y')


class Way(models.Model):
    """Как добраться"""

    place = models.ForeignKey(Place, verbose_name=u'Место отдыха')
    trip = models.CharField(u'Описание', max_length=255)

    class Meta:
        db_table = 'tourism_place_ways'
        verbose_name = u'Маршрут'
        verbose_name_plural = u'Как добраться'

    def __unicode__(self):
        return ''


class Companion(models.Model):
    """Компаньон"""

    COMPOSITION_MY = (
        (1, 'мужчина'),
        (2, 'женщина'),
        (3, 'семья'),
        (4, 'компания'),
    )

    COMPOSITION_FIND = (
        (0, 'кого угодно'),
        (1, 'мужчину'),
        (2, 'женщину'),
        (3, 'семью'),
        (4, 'компанию'),
    )

    author = models.ForeignKey(User, verbose_name=u'Автор', blank=True, null=True, editable=False)
    name = models.CharField(u'Имя', max_length=255)
    about = models.TextField(u'О себе', blank=True)
    my_composition = models.PositiveSmallIntegerField(u'Мой состав', choices=COMPOSITION_MY, default=0)
    find_composition = models.PositiveSmallIntegerField(u'Ищу состав', choices=COMPOSITION_FIND, default=0)
    phone = models.CharField(u'Телефон', max_length=255)
    email = models.EmailField(u'Почта')
    place = models.CharField(u'Место отдыха', max_length=255)
    description = models.TextField(u'Дополнительно', blank=True)
    visible = models.BooleanField(u'Отображение на сайте', default=True)
    created = models.DateTimeField(u'Время создания', auto_now_add=True)

    search = search.CompanionSearch()

    class Meta:
        verbose_name = u'Компаньон'
        verbose_name_plural = u'Компаньоны'

    def __unicode__(self):
        return u'%s для поездки на %s' % (self.name, self.place)


@material_register_signals
class News(news_models.News):
    class Meta:
        proxy = True
        verbose_name = u'новость'
        verbose_name_plural = u'новости раздела'


@material_register_signals
class Article(news_models.Article):
    class Meta:
        proxy = True
        verbose_name = u'статья'
        verbose_name_plural = u'статьи раздела'

    @staticmethod
    def get_material_url(material):
        kwargs = {
            'year': material.stamp.year,
            'month': '%02d' % material.stamp.month,
            'day': '%02d' % material.stamp.day,
            'slug': material.slug,
        }
        return reverse_lazy('tourism:article:read', kwargs=kwargs)


@material_register_signals
class Infographic(news_models.Infographic):
    class Meta:
        proxy = True
        verbose_name = u'инфографика'
        verbose_name_plural = u'инфографика раздела'


@material_register_signals
class Poll(polls_models.Poll):
    class Meta:
        proxy = True
        verbose_name = u'голосование'
        verbose_name_plural = u'голосования раздела'
