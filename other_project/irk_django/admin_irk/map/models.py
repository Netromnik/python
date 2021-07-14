# -*- coding: utf-8 -*-


from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db.models.signals import post_save

from irk.map.cache import invalidate
from irk.options.models import Site
from irk.utils.decorators import deprecated


class Region(models.Model):
    """Регион/область"""

    title = models.CharField(u'Название', max_length=255)

    class Meta:
        db_table = u'map_regions'
        verbose_name = u'регион'
        verbose_name_plural = u'регионы'

    def __unicode__(self):
        return self.title


class Cities(models.Model):
    """Город"""

    id = models.AutoField(primary_key=True)
    region = models.ForeignKey(Region, blank=True, null=True, verbose_name=u'Регион')
    name = models.CharField(u'Имя', unique=True, max_length=180)
    genitive_name = models.CharField(u'Имя в род.п.', max_length=180)
    predl_name = models.CharField(u'Имя в предл.п.', max_length=180)
    alias = models.CharField(u'Алиас', max_length=180, unique=True)
    accuweather_alias = models.CharField(u'Алиас в accuweather.com', max_length=100, blank=True)
    order = models.IntegerField(u'Порядок сортировки')
    datif_name = models.CharField(u'Имя в дат.п.', max_length=180, blank=True)
    phones_code = models.IntegerField(u'Код города')
    cites = models.ManyToManyField(verbose_name=u'Разделы', to=Site, blank=True)
    center = models.PointField(u'Координаты', null=True, blank=True, spatial_index=False)
    weather_label = models.PointField(u'Расположение в погоде', null=True, blank=True, spatial_index=False)
    is_tourism = models.BooleanField(u'Туристический город', default=False)
    news_title = models.CharField(u'Заголовок для новостей', max_length=100, blank=True)
    description = models.TextField(u'Описание города', blank=True)

    objects = models.GeoManager()

    class Meta:
        db_table = u'cities'
        ordering = ('name',)
        verbose_name = u'город'
        verbose_name_plural = u'города'

    def __unicode__(self):
        return self.name


post_save.connect(invalidate, sender=Cities)


class District(models.Model):
    """Район города.

    Например, для Иркутска это Ленинский, Свердловский или Октябрьский районы"""

    city = models.ForeignKey(Cities, related_name='districts', verbose_name=u'Город')
    parent = models.ForeignKey('District', null=True, blank=True, verbose_name=u'Родительский район')
    title = models.CharField(u'Название', max_length=100)
    poly = models.PolygonField(u'Координаты', default='', null=True, spatial_index=False)

    objects = models.GeoManager()

    class Meta:
        db_table = 'map_districts'
        verbose_name = u'район'
        verbose_name_plural = u'районы'

    def __unicode__(self):
        return self.title


# Не используется, но содержит полезную информацию
class Tract(models.Model):
    """Тракт"""

    title = models.CharField(u'Название', max_length=100)
    city = models.ForeignKey(Cities, verbose_name=u'Город', null=True, blank=True)

    class Meta:
        db_table = 'map_tracts'
        verbose_name = u'тракт'
        verbose_name_plural = u'тракты'

    def __unicode__(self):
        return self.title


# Не используется, но содержит полезную информацию
class Countryside(models.Model):
    """Садоводство"""

    TYPE_GARDENING = 1
    TYPE_COTTAGE = 2
    TYPE_CHOICES = (
        (TYPE_GARDENING, u'садоводство'),
        (TYPE_COTTAGE, u'коттеджный поселок'),
    )

    city = models.ForeignKey(Cities, verbose_name=u'Город', null=True, blank=True)
    type = models.PositiveIntegerField(u'Тип', choices=TYPE_CHOICES, default=TYPE_GARDENING)
    tract = models.ForeignKey(Tract, verbose_name=u'Тракт', null=True, blank=True)
    tract_distance = models.IntegerField(u'Километр тракта', null=True, blank=True)
    title = models.CharField(u'Название', max_length=100)
    point = models.PointField(u'Координата', default='', null=True, spatial_index=False)

    objects = models.GeoManager()

    class Meta:
        db_table = 'map_countryside'
        verbose_name = u'садоводство'
        verbose_name_plural = u'садоводства'

    def __unicode__(self):
        return self.title


# Не используется, но содержит полезную информацию
class Cooperative(models.Model):
    """Гаражный кооператив"""

    city = models.ForeignKey(Cities, verbose_name=u'Город', null=True, blank=True)
    title = models.CharField(u'Название', max_length=100)
    point = models.PointField(u'Координата', default='', null=True, spatial_index=False)

    objects = models.GeoManager()

    class Meta:
        db_table = 'map_cooperative'
        verbose_name = u'гаражный кооператив'
        verbose_name_plural = u'гаражные кооперативы'

    def __unicode__(self):
        return self.title


class Streets(models.Model):
    id = models.IntegerField(primary_key=True)
    letter = models.IntegerField()
    name = models.CharField(max_length=765)
    name2 = models.CharField(max_length=765)
    ntype = models.IntegerField(db_column='nType')  # Field name made lowercase.
    placement = models.CharField(max_length=765)
    city = models.ForeignKey(Cities)
    wdev_street = models.PositiveIntegerField(editable=False, null=True, blank=True)  # ID улицы в базе wdev.org

    class Meta:
        db_table = u'streets_main'

    def __unicode__(self):
        try:
            return self.name
        except:
            return u''

    @deprecated
    def get_absolute_url(self):
        return '/ref/street/%s/' % self.pk


class MapHouse(models.Model):
    """Дом на улице

    Слои в базе wdev:
        14, 15, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 53, 54, 60,
        61, 63, 64, 67, 75, 79, 80, 215, 216, 217, 218, 219, 220, 221,
        222, 223, 224, 225, 231
    """

    street = models.ForeignKey(Streets)
    name = models.CharField(max_length=30)
    center = models.PointField(blank=True)
    poly = models.MultiPolygonField()

    objects = models.GeoManager()

    class Meta:
        db_table = 'map_houses'

    def __unicode__(self):
        try:
            return '%s, %s' % (self.street.name, self.name)
        except Streets.DoesNotExist:
            return self.name


ROUTES_TYPES = (
    (1, u'Маршрут транспорта'),
    (2, u'Туристический маршрут'),
)


class Country(models.Model):
    """Страна"""

    title = models.CharField(u'Название', max_length=255)

    class Meta:
        db_table = u'map_countries'
        verbose_name = u'страна'
        verbose_name_plural = u'страны'

    def __unicode__(self):
        return self.title
