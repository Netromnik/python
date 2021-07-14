# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib import admin
from django.utils.html import mark_safe

from irk.game.models import Treasure, Purchase, Progress, Prize, Gamer
from irk.game.helpers import ExpandPrize, ExpandGamer
from irk.game.forms import TreasureAdminForm
from irk.utils.admin import ReadOnlyAdmin


class ReadOnlyTabularInline(admin.TabularInline):
    can_delete = False
    extra = 0
    max_num = 0


class PurchaseInline(ReadOnlyTabularInline):
    model = Purchase
    list_display = ('gamer', 'created')
    readonly_fields = ('gamer', 'created')


class ProgressInline(ReadOnlyTabularInline):
    model = Progress
    list_display = ('tresure', 'created')
    readonly_fields = ('treasure', 'created')


@admin.register(ExpandPrize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'price', 'visible', 'get_amount_left', 'slug')
    list_editable = ('visible',)
    inlines = [PurchaseInline]

    def get_amount_left(self, obj):
        return obj.amount_left()

    get_amount_left.short_description = 'Осталось призов'


@admin.register(Treasure)
class TreasureAdmin(admin.ModelAdmin):
    form = TreasureAdminForm
    list_display = ('name', 'position', 'secret', 'get_image_emoji', 'visible', 'get_url', 'hint')
    list_editable = ('visible', 'position')
    ordering = ('position',)

    def get_url(self, obj):
        return mark_safe('<a href="{url}" target="_blank">{url}</a>'.format(url=obj.url))

    get_url.short_description = 'Ссылка'

    def get_image_emoji(self, obj):
        return mark_safe('<img src="{}" width="20px" height="20px">'.format(obj.svg_emoji))

    get_image_emoji.short_description = 'SVG emoji'


@admin.register(ExpandGamer)
class GamerAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_taked_prize')
    readonly_fields = ('user', 'get_taked_prize')

    inlines = [ProgressInline]

    def get_taked_prize(self, obj):
        return obj.taked_prize()

    get_taked_prize.short_description = 'Взял приз'


@admin.register(Purchase)
class PurchaseAdmin(ReadOnlyAdmin):
    list_display_links = None
    list_display = ('gamer', 'code', 'prize', 'created')


@admin.register(Progress)
class ProgressAdmin(ReadOnlyAdmin):
    list_display_links = None
    list_display = ('gamer', 'treasure', 'created')
