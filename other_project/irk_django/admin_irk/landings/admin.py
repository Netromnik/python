# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.contrib import admin

from irk.gallery.admin import GalleryBBCodeInline, GalleryInline
from irk.landings.forms import Article9MayAdminForm, TreasureDishAdminForm
from irk.landings.models import (Article9May, CovidPage, TreasureDish,
                                 TreasureDishCategory, CovidCard, Thank)
from irk.news.models import Postmeta
from irk.news.tasks import parse_embedded_widgets
from irk.utils.files.admin import admin_media_static


@admin.register(TreasureDish)
class TreasureDishAdmin(admin.ModelAdmin):
    form = TreasureDishAdminForm
    inlines = (GalleryInline,)
    list_display = ('name', 'position', 'category')
    list_editable = ('position',)
    ordering = ('position',)


admin.site.register(TreasureDishCategory)


class PostmetaInline(admin.TabularInline):
    """
    Инлайн для редактирования мета-ключей
    """
    model = Postmeta
    fields = ('key', 'value')  # не показываем лишние поля


@admin.register(CovidPage)
class CovidPageAdmin(admin.ModelAdmin):
    inlines = (GalleryBBCodeInline, PostmetaInline)

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js',)  # для работы галереи

    def save_model(self, request, obj, form, change):
        super(CovidPageAdmin, self).save_model(request, obj, form, change)

        # обработка эмебедов (twitter, instagram, etc)
        # передача id материала не работает, т.к. транзакция
        parse_embedded_widgets.delay(obj.content)


@admin.register(CovidCard)
class CovidCardAdmin(admin.ModelAdmin):
    inlines = (GalleryBBCodeInline, )
    list_display = ('name', 'created', 'visible')
    ordering = ('-created',)

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js',)  # для работы галереи

    def save_model(self, request, obj, form, change):
        super(CovidCardAdmin, self).save_model(request, obj, form, change)

        # обработка эмебедов (twitter, instagram, etc)
        # передача id материала не работает, т.к. транзакция
        parse_embedded_widgets.delay(obj.content)


@admin.register(Article9May)
class Article9MayAdmin(admin.ModelAdmin):
    """Админ статей 9 мая 2020"""
    form = Article9MayAdminForm
    inlines = (GalleryBBCodeInline,)

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js',)  # для работы галереи


@admin.register(Thank)
class ThankAdmin(admin.ModelAdmin):
    """Админ благодарностей докторам"""

    list_display = ('name', 'contact', 'text', 'is_visible', 'created')
