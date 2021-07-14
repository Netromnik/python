# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import render

from irk.gallery.admin import GalleryInline
from irk.news import admin as news_admin
from irk.polls import admin as polls_admin
from irk.tourism import settings
from irk.tourism.forms import PlaceForm, WayForm, TourFirmAdminForm, TourAdminForm
from irk.tourism.forms.firm import TourBaseForm
from irk.tourism.helpers.places import TonkostiRuClient
from irk.tourism.models import Way, Place, TourHotel, TourDate, Tour, Companion, News, Article, Infographic, Poll
from irk.utils.files.admin import admin_media_static
from irk.utils.notifications import tpl_notify
from irk.utils.search.helpers import SearchSignalAdminMixin


class WayInline(admin.TabularInline):
    model = Way
    form = WayForm


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'is_main')
    list_editable = ('is_main',)
    list_filter = ('type', )
    inlines = (WayInline, GalleryInline,)
    form = PlaceForm
    ordering = ('title',)
    search_fields = ('title',)
    fieldsets = (
        (None, {
            'fields': ('parent', 'country', 'title', 'slug', 'type', 'short', 'description', 'extra_description',
                       'content_html', 'position', 'is_main', 'center', 'promo', 'promo_name', 'flag')
        }),
        (u'Привязки к другим сайтам и разделам', {
            'classes': ('collapse',),
            'fields': ('routes', 'nearby', 'yahoo_weather_code', 'weather_popular', 'tonkosti_place_type',
                       'tonkosti_id', 'panorama_url'),
        }),
    )

    @admin_media_static
    class Media(object):
        css = {
            'all': ('css/jquery-ui.css', 'css/admin.css')
        }
        js = (
            'js/apps-js/admin-jq-fix.js',
            'js/apps-js/plugins.js',
            'tourism/js/admin.js',
            'js/apps-js/admin.js',
        )

    def get_urls(self):
        urls = super(PlaceAdmin, self).get_urls()
        my_urls = [
            url(r'^tonkosti/$', self.admin_site.admin_view(self._tonkosti)),
        ]
        return my_urls + urls

    def _tonkosti(self, request):
        client = TonkostiRuClient(settings.TONKOSTI_RU_LOGIN)
        countries = client.countries()
        for country in countries:
            country['regions'] = client.regions(country['id'])

        return render(request, 'tourism/admin/tonkosti.html', {'countries': countries})


class HotelAdmin(SearchSignalAdminMixin, admin.ModelAdmin):
    list_display = ('__unicode__', 'place', 'level', 'category')
    inlines = (GalleryInline,)
    list_select_related = True
    ordering = ('-id',)

    def get_queryset(self, request):
        return super(HotelAdmin, self).get_queryset(request).filter(visible=True)


class TourHotelInline(admin.TabularInline):
    model = TourHotel


class TourDateInline(admin.TabularInline):
    model = TourDate


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_hidden')
    inlines = (TourHotelInline, TourDateInline)
    ordering = ('-id',)
    search_fields = ('title',)
    form = TourAdminForm

    def save_model(self, request, obj, form, change):
        try:
            old_obj = Tour.objects.get(pk=obj.pk)
        except Tour.DoesNotExist:
            old_obj = None
        if old_obj and old_obj.is_hidden and not obj.is_hidden:
            tpl_notify(u'Ваш тур на сайте IRK.ru прошел модерацию', 'tourism/notif/tour/moderated.html',
                       {'object': obj}, request, emails=[obj.firm.user.email, ])
        obj.save()

    @admin_media_static
    class Media(object):
        js = (
            'js/apps-js/admin.js',
        )


class TourBaseAdmin(SearchSignalAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'place', 'price')
    list_select_related = True
    form = TourBaseForm
    ordering = ('-id',)

    @admin_media_static
    class Media(object):
        js = (
            'js/apps-js/admin.js',
        )


class TourFirmAdmin(SearchSignalAdminMixin, admin.ModelAdmin):
    form = TourFirmAdminForm
    ordering = ('-id',)

    @admin_media_static
    class Media(object):
        css = {
            'all': ('tourism/css/admin.css',),
        }
        js = ('tourism/js/admin.js',)


@admin.register(Companion)
class CompanionAdmin(SearchSignalAdminMixin, admin.ModelAdmin):
    pass


@admin.register(News)
class NewsAdmin(news_admin.NewsAdmin, news_admin.SectionMaterialAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(news_admin.ArticleAdmin, news_admin.SectionMaterialAdmin):
    pass


@admin.register(Infographic)
class InfographicAdmin(news_admin.InfographicAdmin, news_admin.SectionMaterialAdmin):
    pass


@admin.register(Poll)
class PollAdmin(polls_admin.PollAdmin, news_admin.SectionMaterialAdmin):
    pass
