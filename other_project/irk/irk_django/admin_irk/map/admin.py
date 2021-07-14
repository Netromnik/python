# -*- coding: utf-8 -*-

from django.contrib import admin

from irk.map.models import Cities, Region, District, Countryside, Tract, Cooperative
from irk.map.forms import CooperativeAdminForm, CountrysideAdminForm
from irk.utils.files.admin import admin_media_static


class CitiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'genitive_name', 'order', 'is_tourism')
    list_editable = ('order', 'is_tourism')
    ordering = ('-id',)


admin.site.register(Cities, CitiesAdmin)


class RegionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('-id',)


admin.site.register(Region, RegionAdmin)


class DistrictAdmin(admin.ModelAdmin):
    """Админ районов города"""

    list_display = ('title', 'city',)
    list_filter = ('city',)
    ordering = ('city', 'title')


admin.site.register(District, DistrictAdmin)


class CountrysideAdmin(admin.ModelAdmin):
    """Админ садоводств города"""

    form = CountrysideAdminForm
    list_display = ('title', 'city',)
    list_filter = ('type', 'city', )
    ordering = ('city', 'title')
    search_fields = ('title', )

    @admin_media_static
    class Media(object):
        js = (
            'js/apps-js/admin.js',
        )


admin.site.register(Countryside, CountrysideAdmin)


class TractAdmin(admin.ModelAdmin):
    """Админ трактов города"""

    list_display = ('title', 'city',)
    list_filter = ('city',)
    ordering = ('city', 'title')


admin.site.register(Tract, TractAdmin)


class CooperativeAdmin(admin.ModelAdmin):
    """Админ гаражных кооперативов"""

    form = CooperativeAdminForm
    list_display = ('title', 'city',)
    list_filter = ('city',)
    ordering = ('city', 'title')
    search_fields = ('title', )

    @admin_media_static
    class Media(object):
        js = (
            'js/apps-js/admin.js',
        )


admin.site.register(Cooperative, CooperativeAdmin)
