# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.urlresolvers import reverse

from irk.utils.files.admin import admin_media_static

from irk.special.models import Project, Sponsor
from irk.special.forms import ProjectAdminForm


class SponsorInline(admin.StackedInline):
    model = Sponsor
    extra = 1
    fields = ('statistic_field', 'project', 'name', 'link', 'image')
    readonly_fields = ('statistic_field',)

    def statistic_field(self, obj):
        if obj.pk:
            return '<a href="{}?sponsor__id__exact={}">Статистика кликов</a>'.format(
                reverse('admin:statistic_specialsponsorclick_changelist'), obj.pk)
        return ''

    statistic_field.allow_tags = True
    statistic_field.short_description = u'Статистика'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    inlines = (SponsorInline,)
    list_display = ('title', 'slug', 'site')

    @admin_media_static
    class Media(object):
        css = {
            'all': ('css/admin.css',),
        }
        js = (
            'js/apps-js/admin.js',
        )
