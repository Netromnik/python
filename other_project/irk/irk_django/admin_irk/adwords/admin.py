# -*- coding: utf-8 -*-

from django.contrib import admin

from irk.adwords.models import AdWord, AdWordPeriod, CompanyNews, CompanyNewsPeriod
from irk.adwords.forms import AdWordForm, AdWordPeriodForm

from irk.gallery.admin import GalleryBBCodeInline
from irk.utils.files.admin import admin_media_static


class AdWordPeriodAdmin(admin.ModelAdmin):
    list_display = ('start', 'end')
    ordering = ('-id',)


class AdWordPeriodInline(admin.TabularInline):
    model = AdWordPeriod
    form = AdWordPeriodForm
    extra = 1


class AdWordAdmin(admin.ModelAdmin):
    inlines = (AdWordPeriodInline, GalleryBBCodeInline)
    form = AdWordForm
    ordering = ('-id',)
    search_fields = ('title',)

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )

admin.site.register(AdWord, AdWordAdmin)


class CompanNewsPeriodInline(admin.TabularInline):
    model = CompanyNewsPeriod
    extra = 1


class CompanyNewsAdmin(admin.ModelAdmin):
    inlines = (CompanNewsPeriodInline, GalleryBBCodeInline,)
    ordering = ('-id',)
    search_fields = ('title', 'caption')
    list_display = ('__unicode__', 'stamp')

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )

admin.site.register(CompanyNews, CompanyNewsAdmin)
