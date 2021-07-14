# -*- coding: utf-8 -*-

from django.contrib import admin

from irk.home.models import Logo
from irk.home.forms import LogoAdminForm, MONTH_NAMES

from irk.utils.files.admin import admin_media_static


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ('title', 'period')
    form = LogoAdminForm
    fieldsets = (
        (None, {
            'fields': ('image', 'title', 'color', 'visible'),
        }),
        (u'Начало показа', {
            'classes': ('lined', 'hide_label'),
            'fields': ('start_month', 'start_day'),
        }),
        (u'Конец показа', {
            'classes': ('lined', 'hide_label'),
            'fields': ('end_month', 'end_day'),
        }),
    )

    def period(self, obj):
        return '%s %s - %s %s' % (MONTH_NAMES[obj.start_month - 1][1],
                                  obj.start_day, MONTH_NAMES[obj.end_month - 1][1], obj.end_day)

    period.short_description = 'Период'

    @admin_media_static
    class Media(object):
        js = ('home/js/admin.js',)
        css = {
            'all': ('css/admin.css',),
        }
