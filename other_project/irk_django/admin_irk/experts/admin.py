# -*- coding: utf-8 -*-

from django.contrib import admin

from irk.experts.models import Expert, Question
from irk.experts.forms import ExpertAdminForm, QuestionInlineAdminForm
from irk.experts.tasks import expert_subscription_send
from irk.news.admin import BaseMaterialAdmin
from irk.options.models import Site

from irk.utils.files.admin import admin_media_static


class QuestionInline(admin.TabularInline):
    model = Question
    form = QuestionInlineAdminForm
    template = 'experts/admin/question_inline.html'
    extra = 0


class ExpertAdmin(BaseMaterialAdmin):
    form = ExpertAdminForm
    list_display = ('admin_change_url', 'category', 'stamp', 'stamp_end', 'stamp_publ', 'questions_count', 'is_answered',
                    'is_consultation')
    list_editable = ('category',)
    search_fields = ('title',)
    # inlines = (QuestionInline,)
    list_per_page = 10

    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic', ),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('hide_comments', 'disable_comments', 'is_hidden', 'is_super', 'is_advertising', 'is_important'),
        }),
        (u'Категории', {
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'project', 'tags')
        }),
        (u'Число дня', {
            'classes': ('collapse',),
            'fields': ('is_number_of_day', 'number_of_day_number', 'number_of_day_text'),
        }),
        (u'Пресс-конференция', {
            'fields': (
                ('is_main', 'is_announce'), ('stamp', 'published_time'), 'stamp_end',
                ('stamp_publ', 'is_answered'), 'user', 'title', 'specialist', 'caption', 'content', 'contacts',
                'avatar', 'signature', 'wide_image', 'image', 'picture', 'image_title', 'firm',
            ),
        }),
    )

    @admin_media_static
    class Media(object):
        js = (
            'js/apps-js/admin.js',
            'experts/js/admin.js',
        )
        css = {
            'all': ('experts/css/admin.css',)
        }

    def save_model(self, request, obj, form, change):
        obj.save()
        if obj.is_answered and not obj.is_consultation:
            expert_subscription_send.delay(obj.pk)

        if not change:
            obj.source_site = Site.objects.get(slugs__icontains='expert')

        super(ExpertAdmin, self).save_model(request, obj, form, change)

    def _get_initial_sites(self, request):
        # Эксперт относятся к новостям

        site = Site.objects.get(slugs__icontains='news')

        return [site.pk]


admin.site.register(Expert, ExpertAdmin)
