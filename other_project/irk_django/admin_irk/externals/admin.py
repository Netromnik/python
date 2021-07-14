# -*- coding: utf-8 -*-

import datetime

from django.contrib import admin

from irk.externals.models import InstagramMedia, InstagramTag, InstagramUserBlacklist
from irk.externals.forms import InstagramMediaAdminForm


class SiteFilter(admin.SimpleListFilter):
    """Фильтр по разделу сайта к которому относятся посты инстаграмма"""

    title = u'Раздел сайта'
    parameter_name = 'site'

    def lookups(self, request, model_admin):
        """Разделы у которых есть посты инстаграмма"""

        qs = model_admin.get_queryset(request)
        params = qs.filter(tags__site__isnull=False).values_list('tags__site', 'tags__site__name').distinct()

        return params

    def queryset(self, request, queryset):
        """Фильтрация по разделу"""

        return queryset.filter(tags__site_id=self.value())


@admin.register(InstagramMedia)
class InstagramMediaAdmin(admin.ModelAdmin):
    list_display = ('_image', '_date', '_user', '_tags', 'is_visible', 'is_marked')
    form = InstagramMediaAdminForm
    list_filter = ('is_visible', 'tags', SiteFilter)

    def _user(self, obj):
        return obj.data['user']['username']
    _user.short_description = u'Автор'

    def _date(self, obj):
        return datetime.datetime.fromtimestamp(int(obj.data['created_time']))
    _date.short_description = u'Дата публикации'

    def _tags(self, obj):
        return u', '.join(obj.tags.all().values_list('title', flat=True))
    _tags.short_description = u'Теги'

    def _image(self, obj):
        return u'<img src="{0[url]}" width="50px" height="50px">'.format(obj.data['images']['thumbnail'])
    _image.short_description = u'Картинка'
    _image.allow_tags = True


@admin.register(InstagramTag)
class InstagramTagAdmin(admin.ModelAdmin):
    list_display = ['name', '_media_count', 'type', 'site', 'is_visible']
    list_filter = ['is_visible']
    list_editable = ['is_visible']

    def _media_count(self, obj):
        """Количество контента"""

        return obj.media.count()
    _media_count.short_description = u'Количество контента'


@admin.register(InstagramUserBlacklist)
class InstagramBlockedUserAdmin(admin.ModelAdmin):
    list_display = ['username']
