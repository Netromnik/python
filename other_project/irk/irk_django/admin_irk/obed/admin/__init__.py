# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin.options import IS_POPUP_VAR
from django.core.urlresolvers import reverse
from django.template.response import SimpleTemplateResponse
from django.utils.html import escape

from irk.news import forms as news_forms
from irk.gallery.admin import GalleryInline
from irk.news import admin as news_admin
from irk.obed.cache import invalidate
from irk.obed.forms import ArticleAdminForm, MenuAdminForm, \
    CorporativeAdminForm, ReviewAdminForm, AwardAdminForm
from irk.obed.models import Type, GuruCause, Article, ArticleCategory, Menu, Review, Dish, Corporative, \
    BarofestParticipant, Award, Poll, Test, SummerTerrace, Delivery, TildaArticle
from irk.polls import admin as polls_admin
from irk.testing import admin as testing_admin
from irk.utils.files.admin import admin_media_static


@admin.register(Article)
class ArticleAdmin(news_admin.ArticleAdmin):
    form = ArticleAdminForm
    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic', ),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': (
                'is_hidden', 'is_super', 'is_advertising', 'main_announcement', 'hide_comments', 'disable_comments'
            ),
        }),
        (u'Категории', {
            'fields': ('sites', ('subject', 'subject_main'), 'type', 'section_category', 'project', 'template')
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_image', 'social_text', 'social_label', 'social_card'),
        }),
        (None, {
            'fields': ('stamp', 'published_time', 'slug', 'title', 'caption', 'content', 'author',
                       'mentions', 'image', 'image_label', 'header_image', 'tags'),
        }),
    )


class DishAdminInline(admin.TabularInline):
    model = Dish
    extra = 1
    fields = ('admin_link', )
    readonly_fields = ('admin_link', )
    template = 'admin/edit_inline/dish_inline.html'

    def admin_link(self, obj):
        if obj.pk:
            changeform_url = reverse('admin:obed_dish_change', args=(obj.pk, ))
            return u'<a href="{}" id="change_inline_dish_{}" onclick="return showDishPopup(this);">' \
                   u'{}</a>'.format(changeform_url, obj.pk, obj.name)
        addform_url = reverse('admin:obed_dish_add')
        return u'<a href="{}" id="add_inline_dish" onclick="return showDishPopup(this);">' \
               u'Добавить еще одно блюдо</a>'.format(addform_url)

    admin_link.allow_tags = True
    admin_link.short_description = ''


@admin.register(Review)
class ReviewAdmin(news_admin.ArticleAdmin):
    form = ReviewAdminForm
    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic', ),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_super', 'is_advertising', 'main_announcement'),
        }),
        (u'Категории', {
            'fields': ('sites', ('subject', 'subject_main'), 'type', 'section_category', 'project', 'template')
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_image', 'social_text', 'social_label', 'social_card'),
        }),
        (None, {
            'fields': (
                'stamp', 'published_time', 'slug', 'title', 'establishment', 'caption', 'content', 'conclusion',
                'resume', 'author', 'mentions', 'image', 'header_image', 'columnist'
            ),
        }),
        (u'Оценка', {
            'fields': ('kitchen', 'service', 'environment')
        }),
    )

    inlines = news_admin.ArticleAdmin.inlines + (DishAdminInline, )

    def save_model(self, request, obj, form, change):

        # Когда меняется привязанное заведение, необходимо очистить рейтинг у старого заведения
        if change and 'establishment' in form.changed_data:
            old_establishment = self.model.objects.get(pk=obj.pk).establishment
            if old_establishment:
                old_establishment.last_review = None
                old_establishment.save()

        super(ReviewAdmin, self).save_model(request, obj, form, change)

        obj.establishment.update_last_review(obj)

    @admin_media_static
    class Media(object):
        js = ('obed/js/admin.js', )


@admin.register(Poll)
class PollAdmin(polls_admin.PollAdmin, news_admin.SectionMaterialAdmin):
    pass


@admin.register(Test)
class TestAdmin(testing_admin.TestAdmin, news_admin.SectionMaterialAdmin):
    pass


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    inlines = (GalleryInline, )

    def response_change(self, request, obj):
        pk_value = obj._get_pk_val()
        if IS_POPUP_VAR in request.POST:
            return SimpleTemplateResponse('admin/popup_dish_response.html', {
                'pk_value': escape(pk_value),
                'obj': obj
            })
        return super(DishAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        pk_value = obj._get_pk_val()
        if IS_POPUP_VAR in request.POST:
            return SimpleTemplateResponse('admin/popup_dish_response.html', {
                'pk_value': escape(pk_value),
                'obj': obj
            })
        return super(DishAdmin, self).response_add(request, obj, post_url_continue=post_url_continue)

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):  # TODO: docstring
    list_display = ('name', 'position')
    list_editable = ('position',)


@admin.register(GuruCause)
class GuruCauseAdmin(admin.ModelAdmin):
    """Админ для Гуру (повод)"""

    list_display = ('name', 'position', 'is_dinner')
    list_editable = ('position',)
    filter_horizontal = ('establishments',)
    fields = ('name', 'position', 'is_dinner', 'establishments')

    @admin_media_static
    class Media(object):
        css = {
            'all': ('obed/css/admin.css',)
        }


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    form = MenuAdminForm
    inlines = (GalleryInline, )

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )


@admin.register(Corporative)
class CorporativeAdmin(admin.ModelAdmin):
    form = CorporativeAdminForm
    inlines = (GalleryInline, )

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )


@admin.register(BarofestParticipant)
class BarofestAdmin(admin.ModelAdmin):
    form = CorporativeAdminForm
    inlines = (GalleryInline, )

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )


@admin.register(SummerTerrace)
class SummerTerraceAdmin(admin.ModelAdmin):
    form = CorporativeAdminForm
    inlines = (GalleryInline, )

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    form = CorporativeAdminForm
    inlines = (GalleryInline, )

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    form = AwardAdminForm
    list_display = ('title', 'establishment', 'caption')
    search_fields = ('title', 'establishment__name', 'establishment__alternative_name')
    fieldsets = (
        (None, {
            'fields': ('title', 'caption', 'icon', 'establishment')
        }),
    )

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )

    def save_model(self, request, obj, form, change):
        super(AwardAdmin, self).save_model(request, obj, form, change)

        invalidate(obj.establishment)


@admin.register(TildaArticle)
class TildaArticleAdmin(news_admin.BaseMaterialAdmin):
    form = news_forms.TildaArticleAdminForm

    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic', ),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': (
                'is_hidden', 'is_super', 'is_advertising', 'is_important',
            ),
        }),
        (u'Категории', {
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'project')
        }),
        (u'Карточка для сетей', {
            'classes': ('collapse',),
            'fields': ('social_buttons', 'social_image', 'social_text', 'social_label', 'social_card'),
        }),
        (None, {
            'fields': ('hide_comments', 'disable_comments', 'stamp', 'published_time', '_schedule_field', 'slug',
                'title', 'caption', 'styles', 'scripts', 'tilda_content', 'author', 'image', 'image_label',
                'archive'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # распаковка архива при импорте
        archive_changed = 'archive' in form.changed_data

        # запишет файл на диск
        super(TildaArticleAdmin, self).save_model(request, obj, form, change)

        if archive_changed and obj.archive:
            obj.import_archive()

admin.site.register(ArticleCategory)
