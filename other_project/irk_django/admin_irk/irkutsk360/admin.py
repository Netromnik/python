# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from irk.irkutsk360.models import Fact, Congratulation


@admin.register(Fact)
class FactAdmin(admin.ModelAdmin):
    list_display = ('number', 'content')
    list_editable = ('number',)
    list_display_links = ('content',)


@admin.register(Congratulation)
class CongratulationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_visible')
