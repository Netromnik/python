# -*- coding: utf-8 -*-

import datetime

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from pytils.dt import ru_strftime

from irk.news.admin import BaseMaterialAdmin
from irk.polls.forms import PollAdminForm, PollChoiceForm
from irk.polls.models import PollChoice, Quiz
from irk.utils.files.admin import admin_media_static
from irk.utils.http import JsonResponse


class PollChoiceInline(admin.TabularInline):
    model = PollChoice
    form = PollChoiceForm
    extra = 1
    verbose_name_plural = u'Ответы'
    template = 'admin/polls/poll_inline_tabular.html'


class PollOpenedFilter(SimpleListFilter):
    title = u'Открыто'
    parameter_name = 'is_opened'

    def lookups(self, request, model_admin):
        return (
            ('0', u'Закрыто'),
            ('1', u'Открыто'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(end__lt=datetime.date.today())
        if self.value() == '1':
            return queryset.filter(end__gte=datetime.date.today())
        return queryset


class PollAdmin(BaseMaterialAdmin):
    form = PollAdminForm
    date_hierarchy = 'start'
    list_display = BaseMaterialAdmin.list_display + ('is_opened', 'start_readable', 'end_readable')
    list_filter = BaseMaterialAdmin.list_filter + (PollOpenedFilter,)
    readonly_fields = BaseMaterialAdmin.readonly_fields + ('votes_cnt',)
    inlines = (PollChoiceInline,)
    date_format = u'%d %B %Y г.'
    ordering = ('-id',)
    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('votes_cnt', 'views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic',),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'multiple',),
        }),
        (u'Категории', {
            'fields': ('sites', 'project', ('target_ct', 'target_id'))
        }),
        (u'Число дня', {
            'classes': ('collapse',),
            'fields': ('is_number_of_day', 'number_of_day_number', 'number_of_day_text'),
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_image', 'social_text', 'social_label', 'social_card'),
        }),
        (None, {
            'fields': (
                'hide_comments', 'disable_comments', ('stamp', 'published_time'), ('start', 'end'), 'title'),
        }),
        (u'Дополнительно', {
            'classes': ('collapse',),
            'fields': (
                'image', 'show_image_on_read', 'image_label', 'w_image', 'caption', 'content', 'tags'),
        }),
    )

    @admin_media_static
    class Media(object):
        css = {
            'all': ('css/admin.css', 'news/css/admin.css', 'polls/css/admin.css',),
        }

        js = ('news/js/admin.js', 'js/apps-js/admin.js', 'polls/js/admin.js',)

    def save_model(self, request, obj, form, change):
        # У голосований нет алиаса, заполняем его id модели или заглушкой
        if not obj.slug:
            obj.slug = obj.pk or 'unknown'

        super(PollAdmin, self).save_model(request, obj, form, change)

    def is_opened(self, obj):
        """Голосование открыто"""

        return obj.end is None or obj.end >= datetime.date.today()

    is_opened.short_description = u'Открыто'
    is_opened.boolean = True

    def start_readable(self, obj):
        """Дата начала голосования в читабельном формате"""

        return ru_strftime(self.date_format, obj.start, inflected=True)

    start_readable.short_description = u'Дата начала'

    def end_readable(self, obj):
        """Дата окончания голосования в читабельном формате"""

        return ru_strftime(self.date_format, obj.end, inflected=True)

    end_readable.short_description = u'Дата конца'

    def get_queryset(self, request):
        return super(PollAdmin, self).get_queryset(request).order_by('-end')

    def get_urls(self):
        return [url(r'^suggest/$', self.admin_site.admin_view(self.suggest))] + super(PollAdmin, self).get_urls()

    def suggest(self, request):
        try:
            content_type = ContentType.objects.get(pk=request.GET.get('ct'))
        except ContentType.DoesNotExist:
            return HttpResponse('')
        try:
            limit = int(request.GET.get('limit'))
        except (TypeError, ValueError):
            limit = 25
        objects = content_type.model_class().objects.all().order_by('-pk')[:limit]

        return JsonResponse([{'id': obj.pk, 'name': unicode(obj)} for obj in objects])


admin.site.register(Quiz)
