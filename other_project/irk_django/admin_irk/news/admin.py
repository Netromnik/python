# -*- coding: utf-8 -*-

import datetime
import logging
import mimetypes
import os

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from irk.gallery.admin import GalleryBBCodeInline, GalleryInline
from irk.news.controllers.socials.social_card import (
    BackgroundSocialCardCreator, PlainSocialCardCreator, PodcastSocialCardCreator, SubjectSocialCardCreator,
    VideoSocialCardCreator
)
from irk.news.forms import (
    ArticleAdminForm, CategoryAdminForm, InfographicAdminForm, LiveAdminForm, LiveEntryForm, MailerAdminForm,
    MetamaterialAdminForm, NewsAdminForm, PhotoAdminForm, PodcastAdminForm, PositionAdminForm, QuoteAdminForm,
    SubjectAdminForm, TildaArticleAdminForm, UrgentNewsAdminForm, VideoAdminForm
)
from irk.news.helpers import split_big_image
from irk.news.models import (
    Article, ArticleType, BaseMaterial, BaseNewsletter, Block, Category, Flash, FlashBlock, Infographic, Live,
    LiveEntry, Mailer, Metamaterial, News, Photo, Podcast, Position, Quote, Subject, UrgentNews, Video,
    ScheduledTask, TildaArticle, Postmeta, material_register_signals
)
from irk.news.tasks import live_entry_image_save, parse_embedded_widgets, social_refresh_cache
from irk.news.tasks import pregenerate_cache as cache_task
from irk.options.models import Site
from irk.utils.decorators import options
from irk.utils.files.admin import admin_media_static
from irk.utils.files.helpers import static_link
from irk.utils.helpers import big_int_from_time
from irk.utils.http import JsonResponse
from irk.utils.notifications import tpl_notify
from irk.utils.search.helpers import SearchSignalAdminMixin

logger = logging.getLogger(__name__)
ailogger = logging.getLogger('article_index')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ категорий новостей"""

    form = CategoryAdminForm
    list_display = ('title', 'is_custom')
    ordering = ('-id',)


class MaterialForSubjectInline(admin.TabularInline):
    model = BaseMaterial
    fields = ['stamp', 'published_time', 'content_type', 'title', 'material_admin_link', 'subject_main']
    readonly_fields = ['stamp', 'published_time', 'title', 'content_type', 'material_admin_link']
    extra = 0
    max_num = 0
    ordering = ['-stamp', '-published_time']
    can_delete = False
    template = 'admin/news/subject/material_inline_tabular.html'

    def material_admin_link(self, obj):
        """Ссылка для редактирования материала в админке"""

        return u'<a href={} target="_blank">{}</a>'.format(obj.content_object.get_admin_url(), u'изменить')
    material_admin_link.short_description = u'Ссылка'
    material_admin_link.allow_tags = True


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Админ сюжетов"""

    form = SubjectAdminForm
    ordering = ['-id']
    list_display = ['title', 'show_on_home', 'is_visible']
    list_editable = ['show_on_home']
    inlines = [MaterialForSubjectInline]
    prepopulated_fields = {'slug': ['title']}
    social_card_creator = SubjectSocialCardCreator
    social_card_fields = ['social_text', 'social_label', 'social_image']

    fieldsets = (
        (None, {
            'fields': ('is_visible', 'title', 'caption_small', 'caption', 'slug', 'background_image', 'show_on_home',
                       'home_image')
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_image', 'social_text', 'social_label', 'social_card'),
        }),
    )

    def save_model(self, request, obj, form, change):

        self._create_social_card(obj, form, change)

        super(SubjectAdmin, self).save_model(request, obj, form, change)

    def _create_social_card(self, obj, form, change):
        """Создать карточку материала для социальных сетей."""

        # Карточка создается для новых объектов или для тех у которых меняется поля с ней связанные.
        if not change or bool(set(form.changed_data) & set(self.social_card_fields)):
            creator = self.social_card_creator(obj)
            creator.create()


class SubjectFilter(admin.SimpleListFilter):
    title = u'Сюжет'
    parameter_name = 'subject'

    def lookups(self, request, model_admin):
        return Subject.objects.all().order_by('-id').values_list('id', 'title')[:20]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(subject=self.value())

        return queryset


class BaseMaterialChangeList(ChangeList):
    """
    Переопределяем базовый ChangeList для оптимизации выборки списка материалов.

    Запрос списка материалов по умолчанию сортируется по полям news_basematerial.stamp и news_news.basematerial_ptr_id.
    Такая сортировка очень медленная. Переопределяем метод get_ordering(), чтобы оптимизировать запрос.
    """

    def get_ordering(self, request, queryset):
        ordering = super(BaseMaterialChangeList, self).get_ordering(request, queryset)

        # Убираем из списка ключ 'pk', чтобы отменить сортировку по basematerial_ptr_id
        # Note: возможны проблемы с пагинацией, если сортировка осуществляется по полю не обеспечивающего четкого
        # порядка для каждой записи (например boolean поле), подробнее https://code.djangoproject.com/ticket/17198
        for item in ordering[:]:
            if item in ('pk', '-pk'):
                ordering.remove(item)

        return ordering

    def get_queryset(self, request):
        qs = super(BaseMaterialChangeList, self).get_queryset(request)

        # Выбираем только нужные поля. Так как в list_display могут содержаться не только поля модели, фильтруем список
        list_display = set(self.list_display)
        available_fields = set(self.opts.get_fields())
        select_fields = list(list_display & available_fields)

        return qs.only(*select_fields)


class SchedulerAdminMixin(object):
    """
    Миксин расширяет админа материала для работы с отложенными публикациями

    После сохранения материала создает таск на публикацию, если дата материала
    в будущем и он скрыт.

    Как включить:

    - Задайте enable_scheduler=True в админе конкретного материала.
      См например: NewsAdmin
    - Замените поле stamp в _list_fields на _stamp
    - Добавьте _schedule_field в fieldsets после published_time
    """

    enable_scheduler = False

    @options(short_description=u'Дата', allow_tags=True)
    def _stamp(self, material):
        """
        Колонка Дата с иконкой календаря для list_display
        """
        icon = ''
        if hasattr(material, 'scheduled_task') and material.scheduled_task.is_scheduled:
            when = material.scheduled_task.when
            icon = '''
                <img src="{1}" title="Опубликуется автоматически в {0:%H}:{0:%M}">
            '''.format(when, static_link('admin/img/icon-calendar.svg'))

        html = '<span class="nowrap">{icon}{dt:%-d} {dt:%B} {dt:%Y} г.</span>'.format(icon=icon, dt=material.stamp)
        return mark_safe(html)

    @options(short_description=u'Запланировать', allow_tags=True)
    def _schedule_field(self, instance):
        """
        Добавьте это поле в fieldsets и в readonly_fields, чтобы вывести интерфейс
        планировщика
        """
        if self.enable_scheduler:
            return mark_safe(render_to_string('admin/news/snippets/schedule_field.html'))
        else:
            return u'Планировщик выключен для этого типа материала'

    def _ensure_task_exists(self, material, when):
        logger.debug(u'Планирование публикации для %s', material)

        try:
            task = material.scheduled_task
        except ScheduledTask.DoesNotExist:
            task = ScheduledTask(material=material)

        task.logmsg(u'Задача запланирована')
        task.state = task.STATE_SCHEDULED
        task.when = when
        task.save()

    def _ensure_task_deleted(self, material):

        try:
            task = material.scheduled_task
            logger.debug(u'Отмена публикации для %s', material)
            # не будем удалять, просто пометим как отмененный - для истории и отладки
            task.logmsg(u'Задача отменена')
            task.state = task.STATE_CANCELED
            task.save()
        except ScheduledTask.DoesNotExist:
            pass

    def _schedule_publication(self, request, material, form, changing):
        """
        Создает/удаляет задачу публикации для материала
        """
        logger.debug(u'Вызов _schedule_publication для %s', material)

        schedule = False
        now = datetime.datetime.now()

        try:
            publication_dt = datetime.datetime.combine(material.stamp, material.published_time)
            if publication_dt > now and material.is_hidden:
                schedule = True
        except TypeError:
            # если не указано время, например
            logger.info(u'Не удается распарсить дату (%s, %s)', material.stamp, material.published_time)

        if schedule:
            self._ensure_task_exists(material, publication_dt)
        else:
            self._ensure_task_deleted(material)

    def save_model(self, request, obj, form, change):
        """
        После сохранения модели ставит задачу в планировщик (если нужно)

        Вызовы идут так:
            BaseMaterialAdmin:save_model()
            SchedulerAdminMixin:save_model()
            admin.ModelAdmin:save_model()
        """
        super(SchedulerAdminMixin, self).save_model(request, obj, form, change)

        # после сохранения
        if self.enable_scheduler:
            self._schedule_publication(request, obj, form, change)


class BaseMaterialAdmin(SchedulerAdminMixin, SearchSignalAdminMixin, VersionAdmin):
    """Базовый админ для всех материалов"""

    list_display = ('admin_change_url', 'views_cnt', '_stamp', 'list_sites', 'is_open', 'is_super', )
    list_display_links = None
    list_select_related = ('scheduled_task',)
    ordering = ['-stamp', '-published_time']
    date_hierarchy = 'stamp'
    search_fields = ('title',)
    inlines = (GalleryBBCodeInline,)
    readonly_fields = (
        'views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt', 'scroll_depth_statistic',
        'social_buttons', '_schedule_field'
    )
    list_per_page = 50

    social_card_creator = BackgroundSocialCardCreator
    social_card_fields = ['social_text', 'social_label', 'social_image', 'image', 'w_image']

    @admin_media_static
    class Media(object):
        css = {
            'all': ('css/admin.css', 'news/css/admin.css'),
        }
        js = (
            'news/js/admin.js', 'js/apps-js/admin.js',
        )

    def save_model(self, request, obj, form, change):

        # При сохранении объекта привязываем его к разделу, в админке которого он был создан
        if not change and not obj.source_site:
            site_slug = request.path.strip('/').split('/')[1]
            obj.source_site = Site.objects.get(slugs__icontains=site_slug)

        self.check_magazine_relations(obj, form)

        # Создать социальную карточку
        material = obj if obj.is_specific() else obj.content_object
        self._create_social_card(material, form, change)

        if 'content' in form.changed_data:
            # Запуск задачи на обработку встраиваемых виджетов в контенте материала (Твиттер и другие)
            # Передача id материала не работает, т.к. на момент вызова задачи транзакция сохранения модели может быть не
            # завершена.
            parse_embedded_widgets.delay(obj.content)

        if change:
            self._update_home_position(obj, form)

        super(BaseMaterialAdmin, self).save_model(request, obj, form, change)

    def get_changeform_initial_data(self, request):
        # Начальные данные для формы
        initial = super(BaseMaterialAdmin, self).get_changeform_initial_data(request)

        initial['sites'] = self._get_initial_sites(request)

        return initial

    def get_changelist(self, request, **kwargs):
        # Переопределяем ChangeList для оптимизации запроса списка материалов

        return BaseMaterialChangeList

    def add_view(self, request, *args, **kwargs):

        result = super(BaseMaterialAdmin, self).add_view(request, *args, **kwargs)

        self._pregenerate_cache(request)

        return result

    def change_view(self, request, *args, **kwargs):
        result = super(BaseMaterialAdmin, self).change_view(request, *args, **kwargs)

        self._pregenerate_cache(request)

        return result

    def changelist_view(self, request, *args, **kwargs):
        result = super(BaseMaterialAdmin, self).changelist_view(request, *args, **kwargs)

        self._pregenerate_cache(request)

        return result

    def delete_view(self, request, *args, **kwargs):
        result = super(BaseMaterialAdmin, self).delete_view(request, *args, **kwargs)

        self._pregenerate_cache(request)

        return result

    @options(short_description=u'Открытая', boolean=True)
    def is_open(self, instance):
        """Статистика доскрола"""
        return not instance.is_hidden

    @options(short_description=u'Разделы', allow_tags=True)
    def list_sites(self, obj):
        return ', '.join([x or u'Главная' for x in obj.sites.all().values_list('name', flat=True)])

    @options(short_description=u'Статистика доскрола', allow_tags=True)
    def scroll_depth_statistic(self, instance):
        """Статистика доскрола"""

        message = u'Открыли: {}\tНачали читать: {} ({:.0%})\tДоскролили до середины: {} ({:.0%})\t' \
                  u'Доскролили до лайков: {} ({:.0%})\tДоскролили до конца: {} ({:.0%})'.replace('\t', '&nbsp;' * 10)

        if hasattr(instance, 'scroll_statistic'):
            s = instance.scroll_statistic
            result = message.format(
                s.point_1,
                s.point_2, (s.point_2 / float(s.point_1)),
                s.point_3, (s.point_3 / float(s.point_1)),
                s.point_4, (s.point_4 / float(s.point_1)),
                s.point_5, (s.point_5 / float(s.point_1)),
            )
        else:
            result = message.format(*([0] * 9))

        return mark_safe(result)

    @options(short_description=u'Заголовок', allow_tags=True)
    def admin_change_url(self, instance):
        """Урл материала в админке"""

        return u'<a href="{}">{}</a>'.format(
            reverse_lazy('admin_redirect', args=(instance.content_type_id, instance.pk)),
            instance.title,
        )

    @options(short_description=u'Размещение в социальных сетях', allow_tags=True)
    def social_buttons(self, instance):
        """Кнопки для размещения в социальных сетях"""

        context = {
            'material_id': instance.id,
            'is_hidden': instance.is_hidden,
        }

        return mark_safe(render_to_string('admin/news/snippets/social_postings_buttons.html', context))

    def _get_initial_sites(self, request):
        """Получить раздел админки в котором создается материал"""

        site_slug = request.path.strip('/').split('/')[1]
        site = Site.objects.get(slugs__icontains=site_slug)

        return [site.pk]

    def _pregenerate_cache(self, request):
        """
        Запуск прегенерации кэша материалов.

        Из-за того, что add_view обернут в transaction.atomic, celery Task получает незакоммиченные данные из БД.
        Поэтому запускать таски нужно после того, как обработан код под transaction.atomic

        Иными словами, этот метод нельзя вызывать из save_model, как другие хуки.
        Его вызывают из add_view и change_view и других похожих.

        :param HttpRequest request: объект запроса
        """

        if request.method == 'POST':
            cache_task.delay(debug_info=request.path)

    def _create_social_card(self, obj, form, change):
        """Создать карточку материала для социальных сетей."""

        # Карточка создается для новых объектов или для тех у которых меняется поля с ней связанные.
        if not change or bool(set(form.changed_data) & set(self.social_card_fields)):
            creator = self.social_card_creator(obj)
            creator.create()
            # Сброс кэша только существующих материалов
            if obj.pk and not obj.is_hidden:
                social_refresh_cache.delay(obj.pk)

    def _update_home_position(self, obj, form):
        """Обновить позицию материала на главной странице"""

        # Обновляем позицию на главной когда:
        # меняется дата публикации
        if 'stamp' in form.changed_data:
            obj.home_position = big_int_from_time()

        # убрана галочка "скрыто"
        if ('is_hidden' in form.changed_data) and (not form.cleaned_data['is_hidden']):
            obj.home_position = big_int_from_time()

    def check_magazine_relations(self, obj, form):
        """Проверка привязки с разделом Журнала"""

        magazine_site = Site.objects.filter(slugs='magazine').first()
        sites = list(form.cleaned_data.get('sites', []))
        if obj.magazine and magazine_site not in sites:
            obj.sites.add(magazine_site)
            # Нужно для form.save_m2m
            form.changed_data.append('sites')
            form.cleaned_data['sites'] = sites + [magazine_site]
        elif not obj.magazine and magazine_site in sites:
            obj.sites.remove(magazine_site)
            sites.remove(magazine_site)
            form.changed_data.append('sites')
            form.cleaned_data['sites'] = sites


class SectionMaterialAdmin(BaseMaterialAdmin):
    """Админ для материалов в разделах"""

    def get_queryset(self, request):
        site_slug = request.path.strip('/').split('/')[1]
        site = Site.objects.get(slugs__icontains=site_slug)

        return super(SectionMaterialAdmin, self).get_queryset(request).filter(source_site=site)

    def has_add_permission(self, request):
        return request.user.has_perm(self.opts.app_label + '.can_change')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm(self.opts.app_label + '.can_change')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm(self.opts.app_label + '.can_delete')


@admin.register(News)
class NewsAdmin(BaseMaterialAdmin):
    """Админ новостей"""

    list_display = ('admin_change_url', 'views_cnt', '_stamp', 'list_sites', 'is_open', 'is_important')
    list_editable = ('is_important',)
    list_filter = ('category', SubjectFilter)
    form = NewsAdminForm

    enable_scheduler = True
    social_card_fields = ['social_text', 'has_video']
    # Класс определяется в методе _create_social_card
    social_card_creator = None

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
                'is_hidden', 'is_exported', 'is_advertising', 'is_important', 'has_video',
                'has_audio', 'is_payed', 'is_auto_disable_comments', 'hide_main_image'
            ),
        }),
        (u'Категории', {
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'city', 'bunch',)
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_buttons', 'social_text', 'social_card'),
        }),
        (u'Официальный комментарий', {
            'classes': ('collapse',),
            'fields': (
                'official_comment_text', 'official_comment_name', 'official_comment_link', 'official_comment_logo',
                'official_comment_bind'
            ),
        }),
        (u'Видео для RSS яндекса', {
            'classes': ('collapse',),
            'fields': (
                'rss_video_preview', 'rss_video_link'
            ),
        }),
        (None, {
            'fields': ('hide_comments', 'disable_comments', 'stamp', 'published_time', '_schedule_field', 'slug',
                       'title', 'caption', 'content', 'author', 'image', 'tags'),
        }),
    )

    def _create_social_card(self, obj, form, change):

        # Для новостей, если стоит галка "Есть видео", то отображаем карточку для видео
        self.social_card_creator = VideoSocialCardCreator if obj.has_video else PlainSocialCardCreator

        super(NewsAdmin, self)._create_social_card(obj, form, change)


class PostmetaInline(admin.TabularInline):
    model = Postmeta
    classes = ['collapse']
    fields = ('key', 'value')


@admin.register(Article)
class ArticleAdmin(BaseMaterialAdmin):
    """Админ статей"""

    form = ArticleAdminForm
    list_display = BaseMaterialAdmin.list_display + ('is_advertising', )
    list_filter = BaseMaterialAdmin.list_filter + ('is_advertising', )

    inlines = BaseMaterialAdmin.inlines + (PostmetaInline,)

    enable_scheduler = True
    social_card_fields = BaseMaterialAdmin.social_card_fields + ['image']

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
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'type', 'project', 'template')
        }),
        (u'Число дня', {
            'classes': ('collapse',),
            'fields': ('is_number_of_day', 'number_of_day_number', 'number_of_day_text'),
        }),
        (u'Журнал', {
            'classes': ('collapse',),
            'fields': ('magazine', 'magazine_author', 'magazine_position', 'magazine_image'),
        }),
        (u'Карточка для сетей', {
            'classes': ('collapse',),
            'fields': ('social_buttons', 'social_image', 'social_text', 'social_label', 'social_card'),
        }),
        (None, {
            'fields': ('hide_comments', 'disable_comments', 'stamp', 'published_time', '_schedule_field', 'slug', 'title', 'caption',
                       'related_material', 'object_id', 'content', 'author', 'image', 'image_label',
                       'header_image', 'tags'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Обновление времени для платной статьи
        try:
            old_obj = Article.objects.get(pk=obj.pk)
        except Article.DoesNotExist:
            old_obj = None
        if (not old_obj or (old_obj and not old_obj.is_paid)) and obj.is_paid:
            obj.paid = datetime.datetime.now()

        # Заполнение поля «Введение»
        obj.fill_introduction(save=False)

        super(ArticleAdmin, self).save_model(request, obj, form, change)


@admin.register(Video)
class VideoAdmin(BaseMaterialAdmin):
    """Админ видео"""

    form = VideoAdminForm
    social_card_creator = VideoSocialCardCreator
    enable_scheduler = True

    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic', ),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_super', 'is_advertising', 'is_important'),
        }),
        (u'Категории', {
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'project')
        }),
        (u'Число дня', {
            'classes': ('collapse',),
            'fields': ('is_number_of_day', 'number_of_day_number', 'number_of_day_text'),
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_text', 'social_card'),
        }),
        (None, {
            'fields': ('hide_comments', 'disable_comments', 'stamp', 'published_time', '_schedule_field', 'slug', 'title', 'caption',
                       'content', 'author', 'preview', 'tags'),
        }),
    )


@admin.register(Photo)
class PhotoAdmin(BaseMaterialAdmin):
    """Админ фоторепортажей"""

    form = PhotoAdminForm
    list_display = BaseMaterialAdmin.list_display + ('is_advertising',)
    list_filter = BaseMaterialAdmin.list_filter + ('is_advertising', )
    list_editable = BaseMaterialAdmin.list_editable + ('is_advertising', )
    enable_scheduler = True

    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic',),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_super', 'is_advertising', 'is_important'),
        }),
        (u'Категории', {
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'project')
        }),
        (u'Число дня', {
            'classes': ('collapse',),
            'fields': ('is_number_of_day', 'number_of_day_number', 'number_of_day_text'),
        }),
        (u'Журнал', {
            'classes': ('collapse',),
            'fields': ('magazine', 'magazine_author', 'magazine_position', 'magazine_image'),
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_image', 'social_text', 'social_label', 'social_card'),
        }),
        (None, {
            'fields': ('hide_comments', 'disable_comments', 'stamp', 'published_time', 'slug', 'title', 'caption',
                       'caption_short', 'share_text', 'content', 'author', 'image', 'tags'),
        }),
    )


@admin.register(Infographic)
class InfographicAdmin(BaseMaterialAdmin):
    """Админ инфографики"""

    form = InfographicAdminForm
    enable_scheduler = True

    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic', ),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_super', 'is_advertising', 'is_important'),
        }),
        (u'Категории', {
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'project')
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
            'fields': ('hide_comments', 'disable_comments', 'title', 'caption', 'preview', 'image', 'thumbnail',
                       'iframe_url', 'iframe_height', 'stamp', 'published_time', '_schedule_field', 'tags', 'author'),
        }),
    )

    def save_model(self, request, obj, form, change):
        super(InfographicAdmin, self).save_model(request, obj, form, change)
        split_big_image(obj.image.path)


@admin.register(Metamaterial)
class MetamaterialAdmin(BaseMaterialAdmin):
    """Админ метаматериалов"""

    form = MetamaterialAdminForm
    enable_scheduler = True

    fieldsets = (
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_super', 'is_special', 'show_on_home'),
        }),
        (u'Категории', {
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'project')
        }),
        (u'Число дня', {
            'classes': ('collapse',),
            'fields': ('is_number_of_day', 'number_of_day_number', 'number_of_day_text'),
        }),
        (None, {
            'fields': ('hide_comments', 'disable_comments', 'stamp', 'published_time', '_schedule_field', 'url', 'slug', 'title',
                       'caption', 'image', 'image_3x2', 'tags'),
        }),
    )


@admin.register(Podcast)
class PodcastAdmin(BaseMaterialAdmin):
    """Админ подкастов"""
    form = PodcastAdminForm
    enable_scheduler = True
    social_card_creator = PodcastSocialCardCreator

    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_super'),
        }),
        (u'Категории', {
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'project')
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_text', 'social_label', 'social_card'),
        }),
        (None, {
            'fields': (
                'hide_comments', 'disable_comments', 'stamp', 'published_time', '_schedule_field', 'slug', 'title', 'link', 'caption',
                'content', 'author', 'tags'
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Заполнение поля «Введение»
        obj.fill_introduction(save=False)

        super(PodcastAdmin, self).save_model(request, obj, form, change)


@admin.register(ArticleType)
class ArticleTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Flash)
class FlashAdmin(admin.ModelAdmin):
    list_display = ('flash_title', 'type', 'visible', 'created')
    readonly_fields = ['author']
    list_filter = ('type', 'visible')
    list_editable = ('visible',)
    inlines = (GalleryInline,)
    ordering = ('-id',)

    @options(short_description=u'Заголовок')
    def flash_title(self, obj):
        if obj.is_site:
            return obj.title
        return obj.content

    @admin_media_static
    class Media(object):
        css = {
            'all': ('css/admin.css', 'news/css/admin.css'),
        }
        js = (
            'news/js/admin.js', 'js/apps-js/admin.js',
        )


@admin.register(Mailer)
class MailerAdmin(admin.ModelAdmin):
    list_display = ('title', 'stamp')
    list_display_links = ('title',)

    form = MailerAdminForm

    def has_change_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.save()
        self.send_mail(request, obj)

    def send_mail(self, request, obj):
        mails = obj.mails.split(',')
        if obj.file:
            ext = os.path.splitext(obj.file.file.name)[1]
            mime_type = mimetypes.guess_type(obj.file.file.name)[0]
            attachment = [("file%s" % ext, obj.file.file.read(), mime_type)]
        else:
            attachment = None
        for mail in mails:
            mail = mail.strip()
            sender = u'Твой Иркутск <news@irk.ru>'
            tpl_notify(obj.title, 'news/notif/mailer.html', {
                'title': obj.title,
                'text': obj.text,
            }, request, emails=(mail,), sender=sender, attachments=attachment)


@admin.register(Live)
class LiveAdmin(admin.ModelAdmin):
    """Админка онлайн-трансляций"""

    list_display = ('news',)
    list_select_related = True
    form = LiveAdminForm

    @admin_media_static
    class Media:
        js = ('js/lib/jquery-1.7.2.min.js',)

    def get_urls(self):
        return [
            url(r'^(?P<object_id>\d+)/change/online/$', self.admin_site.admin_view(self.live_view)),
            url(r'^(?P<object_id>\d+)/change/online/(?P<entry_id>\d+)/$', self.admin_site.admin_view(self.live_entry_view)),
            url(r'^(?P<object_id>\d+)/change/online/(?P<entry_id>\d+)/delete/$', self.admin_site.admin_view(self.delete_entry_view)),
            url(r'^(?P<object_id>\d+)/change/online/update/$', self.admin_site.admin_view(self.live_update_view)),
        ] + super(LiveAdmin, self).get_urls()

    def live_view(self, request, object_id):
        live = get_object_or_404(Live, pk=object_id)

        if request.POST:
            form = LiveEntryForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                instance = form.save(commit=False)
                if not instance.created:
                    instance.created = datetime.datetime.now().time()
                instance.live = live
                instance.save()

                if '[image' in instance.text:
                    live_entry_image_save.delay(instance.pk)
                    messages.info(request, u'Изображения из сообщения скоро будут добавлены в трансляцию')
                return redirect('.')

        else:
            form = LiveEntryForm()

        entries = live.entries.all().order_by('-date', '-created')

        context = {
            'form': form,
            'object': live,
            'entries': entries,
        }

        return render(request, 'admin/news/live/online_view.html', context)

    def live_update_view(self, request, object_id):
        live = get_object_or_404(Live, pk=object_id)

        response = []
        for entry in live.entries.all().order_by('-date', '-created'):
            response.append({
                'id': entry.pk,
                'created': entry.created.strftime('%H:%M'),
                'date': entry.date.strftime('%Y-%m-%d'),
                'text': entry.text,
                'image': entry.image.url if entry.image else '',
                'is_important': entry.is_important,
            })

        return JsonResponse(response)

    def delete_entry_view(self, request, object_id, entry_id):
        entry = get_object_or_404(LiveEntry, pk=entry_id)
        entry.delete()

        return JsonResponse({'status': 'ok'})

    def live_entry_view(self, request, object_id, entry_id):
        live = get_object_or_404(Live, pk=object_id)
        entry = get_object_or_404(LiveEntry, live=live, pk=entry_id)
        if request.POST:
            form = LiveEntryForm(data=request.POST, files=request.FILES, instance=entry)
            if form.is_valid():
                form.save()

                return redirect('..')

        else:
            form = LiveEntryForm(instance=entry, initial={'created':entry.created})

        context = {
            'live': live,
            'entry': entry,
            'form': form,
        }

        return render(request, 'admin/news/live/entry_view.html', context)


@admin.register(UrgentNews)
class UrgentNewsAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_visible', 'created')
    list_editable = ('is_visible',)
    ordering = ('-id',)
    form = UrgentNewsAdminForm

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created = datetime.datetime.now()
        obj.save()


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    form = QuoteAdminForm

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', 'news/js/admin.js')


class PositionInline(admin.TabularInline):
    form = PositionAdminForm
    model = Position

    def get_max_num(self, request, obj=None, **kwargs):
        if obj:
            # Количество форм определяем на основе поля Block.position_count
            return obj.position_count
        else:
            return self.max_num


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):

    inlines = (PositionInline, )

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', 'news/js/admin.js')


@admin.register(BaseNewsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Админ новостных рассылок"""

    list_display = ('__unicode__', 'materials_count', 'sent_cnt', 'views_cnt', 'status', 'sent')
    list_display_links = None
    list_filter = ('status', )

    def get_queryset(self, request):
        return super(NewsletterAdmin, self).get_queryset(request).select_subclasses()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @options(short_description=u'Материалы')
    def materials_count(self, obj):
        """Количество материалов в рассылке"""

        return u'{}'.format(obj.materials.count())


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    """Админ запланированных задач"""

    list_select_related = ('material',)
    list_display = ('material', 'when', 'task', 'updated', 'state')
    fields = ('material_link', 'when', 'task', 'updated', 'state', 'log')
    readonly_fields = ('material_link', 'updated')

    @options(short_description=u'Материал', allow_tags=True)
    def material_link(self, obj):
        material = obj.material
        return u'<a href="{}">{}</a>'.format(
            reverse_lazy('admin_redirect', args=(material.content_type_id, material.pk)),
            material.title,
        )


def register_other_materials():
    """
    Регистрация прокси модели и админки для материалов из других разделов

    Нормально объявить эти классы мешает циклический импорт на news.models
    """
    from irk.polls import admin as polls_admin
    from irk.polls import models as polls_models
    from irk.testing import models as testing_models
    from irk.testing import admin as testing_admin

    @material_register_signals
    class Poll(polls_models.Poll):
        class Meta:
            proxy = True
            verbose_name = u'голосование'
            verbose_name_plural = u'голосования раздела'

    @material_register_signals
    class Test(testing_models.Test):
        class Meta:
            proxy = True
            verbose_name = u'тест'
            verbose_name_plural = u'тесты раздела'

    class PollAdmin(polls_admin.PollAdmin, SectionMaterialAdmin):
        pass

    class TestingAdmin(testing_admin.TestAdmin, SectionMaterialAdmin):
        pass

    admin.site.register(Poll, PollAdmin)
    admin.site.register(Test, TestingAdmin)


register_other_materials()
admin.site.register(FlashBlock)

@admin.register(TildaArticle)
class TildaArticleAdmin(BaseMaterialAdmin):
    form = TildaArticleAdminForm

    enable_scheduler = True
    social_card_fields = BaseMaterialAdmin.social_card_fields + ['image']

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
                'tags', 'archive'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # распаковка архива при импорте
        archive_changed = 'archive' in form.changed_data

        # запишет файл на диск
        super(TildaArticleAdmin, self).save_model(request, obj, form, change)

        if archive_changed and obj.archive:
            obj.import_archive()
