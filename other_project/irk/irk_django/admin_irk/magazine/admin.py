# -*- coding: utf-8 -*-

from django.contrib import admin

from irk.magazine.models import Magazine, MagazineAuthor
from irk.magazine.forms import MagazineAdminForm
from irk.news.models import BaseMaterial
from irk.utils.decorators import options
from irk.utils.files.admin import admin_media_static


class MaterialForMagazineInline(admin.TabularInline):
    model = BaseMaterial
    fields = ['stamp', 'published_time', 'content_type', 'title', 'material_admin_link', 'magazine_position']
    readonly_fields = ['stamp', 'published_time', 'title', 'content_type', 'material_admin_link']
    extra = 0
    max_num = 0
    ordering = ['magazine_position']
    can_delete = False
    template = 'admin/news/subject/material_inline_tabular.html'

    @options(allow_tags=True, short_description=u'Ссылка')
    def material_admin_link(self, obj):
        """Ссылка для редактирования материала в админке"""

        return u'<a href={} target="_blank">{}</a>'.format(obj.cast().get_admin_url(), u'изменить')


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    form = MagazineAdminForm
    list_display = ('title', 'show_on_home')
    inlines = [MaterialForMagazineInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'caption', 'slug', 'visible', 'show_on_home', 'home_image', 'caption_author',
                       'branding_bottom', 'banner_right', 'banner_comment')
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_image', 'social_text', 'social_label', 'social_card'),
        }),
    )

    @admin_media_static
    class Media(object):
        css = {
            'all': ('css/admin.css',),
        }
        js = (
            'js/apps-js/admin.js',
        )

@admin.register(MagazineAuthor)
class MagazineAuthorAdmin(admin.ModelAdmin):
    pass
