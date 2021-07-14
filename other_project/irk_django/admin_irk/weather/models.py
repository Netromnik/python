# -*- coding: utf-8 -*-

"""
Данные представлены в основном в числовом виде на основе справочника weather_config.yaml
"""

import pytils
from django.contrib.gis.db import models
from django.db.models.signals import post_save

from irk.map import models as map_models
from irk.utils.fields.file import ImageRemovableField
from irk.weather.cache import invalidate
from irk.weather.managers import WishForConditionsQuerySet


class WeatherCities(models.Model):
    """
    Прогноз погоды по городу на день.
    """

    id = models.IntegerField(primary_key=True)
    date = models.DateField(u'дата')
    day = models.IntegerField(u'дневная', null=True, blank=True)
    night = models.IntegerField(u'ночная', null=True, blank=True)
    wind = models.IntegerField(u'скорость ветра', null=True, blank=True)
    wind_t = models.IntegerField(u'направление ветра', null=True, blank=True)
    nebulosity = models.IntegerField(u'облачность', null=True, blank=True)
    precipitation = models.IntegerField(u'осадки', null=True, blank=True)
    sun_v = models.TimeField(u'восход', null=True, blank=True)
    sun_z = models.TimeField(u'заход', null=True, blank=True)
    stamp = models.DateTimeField(u'временная метка', null=True)
    source = models.IntegerField(u'источник данных')  # Не используется

    city = models.ForeignKey(map_models.Cities, db_column='city', verbose_name=u'город')

    class Meta:
        db_table = u'weather_cities'

    def __unicode__(self):
        return u'{0.date}. {0.city} temp: {0.day} wind: {0.wind}'.format(self)


post_save.connect(invalidate, sender=WeatherCities)


class WeatherFact(models.Model):
    """Фактическая погода на момент времени"""

    id = models.IntegerField(primary_key=True)
    datetime = models.DateTimeField(u'дата и время')
    day = models.IntegerField(u'день', help_text=u'В формате %m%d')
    temp = models.IntegerField(u'температура', null=True, blank=True)
    temp_feel = models.IntegerField(u'Температура по ощущениям', null=True, blank=True)  # Не используется
    weather_code = models.IntegerField(u'код описания погоды', null=True, blank=True)  # Не используется
    nebulosity = models.IntegerField(u'облачность', null=True, blank=True)
    mm = models.IntegerField(u'давление', null=True, blank=True)
    wind = models.IntegerField(u'скорость ветра', null=True, blank=True)
    wind_t = models.IntegerField(u'направление ветра', null=True, blank=True)  # Не используется
    humidity = models.IntegerField(u'влажность', null=True, blank=True)
    visibility = models.PositiveIntegerField(u'Видимость, м.', null=True, blank=True)

    city = models.IntegerField(null=True, blank=True, verbose_name=u'город')

    class Meta:
        db_table = u'weather_fact'

    def __unicode__(self):
        return u'{0.datetime}. {0.city} temp: {0.temp} wind: {0.wind}'.format(self)


post_save.connect(invalidate, sender=WeatherFact)


class WeatherDetailed(models.Model):
    """Детальная погода по городу с периодом 3 часа"""

    datetime = models.DateTimeField(u'дата и время')
    day = models.PositiveIntegerField(u'число', db_index=True)
    hour = models.PositiveIntegerField(u'час')
    wind = models.IntegerField(u'скорость ветра', null=True, blank=True)
    wind_t = models.IntegerField(u'направление ветра', null=True, blank=True)
    temp_from = models.IntegerField(u'температура от', null=True, blank=True)
    temp_to = models.IntegerField(u'температура до', null=True, blank=True)
    temp_feel = models.IntegerField(u'Температура по ощущениям', null=True, blank=True)  # Не используется
    mm = models.PositiveIntegerField(u'давление', null=True, blank=True)
    humidity = models.PositiveIntegerField(u'влажность', null=True, blank=True)
    nebulosity = models.IntegerField(u'облачность', null=True, blank=True)
    precipitation = models.IntegerField(u'осадки', null=True, blank=True)

    city = models.ForeignKey(map_models.Cities, verbose_name=u'город')

    class Meta:
        db_table = u'weather_detailed'

    def __unicode__(self):
        return u'{0.datetime} {0.hour}. {0.city} temp: {0.temp_feel} wind: {0.wind}'.format(self)


post_save.connect(invalidate, sender=WeatherDetailed)


class WeatherSigns(models.Model):
    """Приметы"""

    month = models.IntegerField(u'Месяц', choices=zip(range(1, 13), [month[1] for month in pytils.dt.MONTH_NAMES]))
    day = models.IntegerField(u'День')
    text = models.TextField(u'Текст')

    class Meta:
        db_table = u'weather_signs'
        verbose_name = u'примету'
        verbose_name_plural = u'приметы'


post_save.connect(invalidate, sender=WeatherSigns)


class WeatherTempHour(models.Model):
    """Температура и давление в городах по часам"""

    temp = models.IntegerField(u'температура')
    time = models.DateTimeField(u'дата и время')
    place = models.IntegerField(u'место')  # Не используется
    city = models.IntegerField(u'город')
    mm = models.IntegerField(u'давление', null=True, blank=True)

    class Meta:
        db_table = u'weather_temp_hour'


post_save.connect(invalidate, sender=WeatherTempHour)


class MeteoCentre(models.Model):
    """Прогноз погоды от Иркутского гидрометцентра"""

    stamp = models.DateField(u'Дата', unique=True)
    content = models.TextField(u'Текст', blank=True)
    storm_caption = models.CharField(u'Описание штормового', max_length=20, blank=True)
    storm_content = models.TextField(u'Штормовое', max_length=125, blank=True)

    class Meta:
        db_table = u'weather_meteocentre'
        verbose_name = u'прогноз гидрометеоцентра'
        verbose_name_plural = u'прогноз гидрометеоцентра'

    def __unicode__(self):
        return u'Прогноз гидрометеоцентра на %s' % self.stamp.strftime('%d.%m.%Y')

    def is_storm(self):
        """Штормовое предупреждение?"""

        return bool(self.storm_caption)


post_save.connect(invalidate, sender=MeteoCentre)


class FirePlace(models.Model):
    """Данные о пожарной обстановке"""

    center = models.PointField(u'Координаты', spatial_index=False)
    created = models.DateTimeField(u'Дата обновления')

    objects = models.GeoManager()

    class Meta:
        db_table = u'weather_fireplaces'
        verbose_name = u'лесной пожар'
        verbose_name_plural = u'лесные пожары'


class WishBase(models.Model):
    """Базовый класс для всех пожеланий"""

    image = ImageRemovableField(
        verbose_name=u'изображение', upload_to='img/site/weather/wishes/',
        help_text=u'Размер 1920x440')  # min_size=(1920, 440), max_size=(1920, 440),
    text = models.TextField(u'текст')

    class Meta:
        abstract = True


class WishForDay(WishBase):
    """Пожелание для города на день"""

    date = models.DateField(u'дата', db_index=True)

    class Meta:
        verbose_name = u'пожелание на день'
        verbose_name_plural = u'пожелания на день'
        unique_together = ['date']

    def __unicode__(self):
        return u'Пожелание на {}'.format(self.date)


post_save.connect(invalidate, sender=WishForDay)


class WishForConditions(WishBase):
    """Пожелание по погодным условиям"""

    months = models.ManyToManyField('Month', verbose_name=u'месяца', blank=True)
    t_min = models.IntegerField(u'мин температура', null=True, blank=True)
    t_max = models.IntegerField(u'макс температура', null=True, blank=True)
    is_storm = models.BooleanField(u'штормовое', db_index=True, default=False)
    is_strong_wind = models.BooleanField(
        u'сильный ветер', db_index=True, default=False, help_text=u'Больше 15 м/с (включительно)'
    )
    is_cloudy = models.BooleanField(u'облачно или пасмурно', db_index=True, default=False)
    is_precipitation = models.BooleanField(u'осадки', db_index=True, default=False)
    is_variable = models.BooleanField(u'переменная облачность', db_index=True, default=False)

    is_active = models.BooleanField(u'активно', db_index=True, default=True)

    conditions = WishForConditionsQuerySet.as_manager()

    class Meta:
        verbose_name = u'Пожелание по условиям'
        verbose_name_plural = u'Пожелания по условиям'

    def __unicode__(self):
        return u'Пожелание по условиям #{}'.format(self.id)


post_save.connect(invalidate, sender=WishForConditions)


class Month(models.Model):
    """Календарный месяц"""

    name = models.CharField(u'название', max_length=30, unique=True)
    alias = models.CharField(u'алиас', max_length=15, db_index=True)
    number = models.PositiveSmallIntegerField(u'порядковый номер', help_text=u'Отсчет с нуля', db_index=True)

    class Meta:
        verbose_name = u'Месяц'
        verbose_name_plural = u'Месяца'
        ordering = ['number']

    def __unicode__(self):
        return u'{}'.format(self.name)


class MoonDay(models.Model):
    """Лунный день календаря"""

    AFFECT_TERRIBLE = 1
    AFFECT_BAD = 2
    AFFECT_NORMAL = 3
    AFFECT_GOOD = 4
    AFFECT_EXCELLENT = 5

    AFFECTS = (
        (AFFECT_TERRIBLE, u'ужасно'),
        (AFFECT_BAD, u'плохо'),
        (AFFECT_NORMAL, u'норма'),
        (AFFECT_GOOD, u'хорошо'),
        (AFFECT_EXCELLENT, u'отлично'),
    )

    number = models.PositiveSmallIntegerField(u'номер', unique=True)
    title = models.CharField(u'заголовок', max_length=50, blank=True)
    symbol = models.CharField(u'символ', max_length=50, blank=True)
    stones = models.CharField(u'камни', max_length=100, blank=True)
    content = models.TextField(u'описание', blank=True)

    for_undertaking = models.PositiveSmallIntegerField(u'начинания', choices=AFFECTS, null=True, blank=True)
    for_money = models.PositiveSmallIntegerField(u'деньги', choices=AFFECTS, null=True, blank=True)
    for_dream = models.PositiveSmallIntegerField(u'сны', choices=AFFECTS, null=True, blank=True)
    for_housework = models.PositiveSmallIntegerField(u'домашние дела', choices=AFFECTS, null=True, blank=True)
    for_haircut = models.PositiveSmallIntegerField(u'стрижка', choices=AFFECTS, null=True, blank=True)
    for_drink = models.PositiveSmallIntegerField(u'застолье', choices=AFFECTS, null=True, blank=True)

    class Meta:
        verbose_name = u'лунный день'
        verbose_name_plural = u'лунные дни'
        ordering = ['number']

    def __unicode__(self):
        return u'{} лунный день'.format(self.number)


class MoonTiming(models.Model):
    """График лунных дней"""

    start_date = models.DateTimeField(u'начало', db_index=True)
    end_date = models.DateTimeField(u'конец', db_index=True)
    number = models.PositiveSmallIntegerField(u'номер')

    class Meta:
        verbose_name = u'запись лунного графика'
        verbose_name_plural = u'лунный график'
        ordering = ['start_date']

    def __unicode__(self):
        return u'{0.start_date:%d.%m.%Y %H:%M} - {0.end_date:%d.%m.%Y %H:%M}: {0.number} лунный день'.format(self)

    @classmethod
    def moon_day_number(cls, stamp):
        """Возвращает номер лунного дня для метки времени"""

        return cls.objects.filter(start_date__lte=stamp, end_date__gt=stamp).values_list('number', flat=True).first()


class Joke(models.Model):
    """Анекдот дня"""

    month = models.PositiveSmallIntegerField(
        u'месяц', choices=zip(range(1, 13), [month[1] for month in pytils.dt.MONTH_NAMES]), db_index=True
    )
    day = models.PositiveSmallIntegerField(u'день', db_index=True)
    content = models.TextField(u'текст')

    class Meta:
        verbose_name = u'анекдот'
        verbose_name_plural = u'анекдоты'
        unique_together = ('month', 'day')
