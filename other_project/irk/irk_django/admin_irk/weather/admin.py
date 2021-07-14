# -*- coding: utf-8 -*-

import datetime
from pytils.dt import ru_strftime

from django.contrib import admin
from django.template.defaultfilters import truncatewords

from irk.weather import models


@admin.register(models.WeatherSigns)
class WeatherSignsAdmin(admin.ModelAdmin):
    list_display = ('date', 'text')
    list_display_links = ('text',)
    list_filter = ('month',)

    def date(self, object):
        year = datetime.date.today().year
        # На случай, если генерируемой даты нет в этом году
        for i in range(0, 4):
            try:
                return ru_strftime(u'%d %B', datetime.datetime(year+i, int(object.month), int(object.day)),
                                   inflected=True)
            except ValueError:
                continue
    date.short_description = u'Дата'


@admin.register(models.MeteoCentre)
class MeteoCentreAdmin(admin.ModelAdmin):
    list_display = ('date_link',)
    ordering = ('-stamp',)

    def date_link(self, obj):
        return u'<a href="./%s/">%s</a>' % (obj.pk, ru_strftime(u'%d %B %Y г.', obj.stamp, inflected=True))
    date_link.allow_tags = True
    date_link.short_description = u'Дата'


@admin.register(models.WishForDay)
class WishForDayAdmin(admin.ModelAdmin):
    list_display = ('_image', 'date')

    def _image(self, obj):
        return u'<img src="{0}" width="200px">'.format(obj.image.url)
    _image.short_description = u'Картинка'
    _image.allow_tags = True


@admin.register(models.WishForConditions)
class WishForConditionsAdmin(admin.ModelAdmin):
    list_display = (
        '_image', '_months', 't_min', 't_max', 'is_storm', 'is_strong_wind', 'is_cloudy', 'is_variable',
        'is_precipitation', 'is_active'
    )
    list_filter = ['months']
    list_editable = ['is_active']
    filter_horizontal = ['months']
    fieldsets = (
        (None, {
            'fields': ('image', 'text', 'is_active'),
        }),
        (u'Условия', {
            'fields': (
                ('t_min', 't_max'), 'is_storm', 'is_strong_wind', 'is_cloudy', 'is_variable', 'is_precipitation',
                'months'
            )
        }),
    )

    def _image(self, obj):
        return u'<img src="{0}" width="200px">'.format(obj.image.url)
    _image.short_description = u'Картинка'
    _image.allow_tags = True

    def _months(self, obj):
        return u', '.join(m.name for m in obj.months.all())
    _months.short_description = u'Месяца'


@admin.register(models.MoonDay)
class MoodDayAdmin(admin.ModelAdmin):
    """Админка лунного календаря"""

    pass


@admin.register(models.Joke)
class JokeAdmin(admin.ModelAdmin):
    """Админка анекдотов"""

    list_display = ('date', 'title')
    list_display_links = ('title',)
    list_filter = ('month',)

    def date(self, obj):
        year = datetime.date.today().year
        # На случай, если генерируемой даты нет в этом году
        for i in range(0, 4):
            try:
                return ru_strftime(u'%d %B', datetime.datetime(year+i, int(obj.month), int(obj.day)),
                                   inflected=True)
            except ValueError:
                continue
    date.short_description = u'Дата'

    def title(self, obj):
        return truncatewords(obj.content, 25)
    title.short_description = u'Содержание'
