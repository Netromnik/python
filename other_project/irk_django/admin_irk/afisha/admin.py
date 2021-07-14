# -*- coding: utf-8 -*-

import datetime
import logging

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.utils.safestring import mark_safe

from irk.afisha.forms.admin import (
    AnnouncementAdminInlineForm, EventForm, EventGuideForm, GuideEventGuideForm, GuideForm, PaginatedFormSet,
    PrismAdminForm, ReviewAdminForm, TicketBuildingChangeListAdminForm, TicketEventChangeListAdminForm,
    TicketHallChangeListAdminForm
)
from irk.afisha.models import (
    Announcement, AnnouncementColor, Article, Event, EventGuide, EventType, Genre, Guide, Hall, KassyBuilding,
    KassyEvent, KassyRollerman, Photo, Poll, Prism, RamblerEvent, RamblerHall, Review, Test, EventOrder, Period, Sessions
)
from irk.afisha.tasks import bind_ticket_sessions, unbind_ticket_sessions
from irk.afisha.tickets.binder import TicketBinder
from irk.afisha.order_helpers import EventOrderHelper
from irk.gallery.admin import GalleryInline
from irk.news import admin as news_admin
from irk.polls import admin as polls_admin
from irk.testing import admin as testing_admin
from irk.utils.decorators import options
from irk.utils.files.admin import admin_media_static
from irk.utils.helpers import inttoip
from irk.utils.search.helpers import SearchSignalAdminMixin

logger = logging.getLogger(__name__)

admin.site.register(Genre)


class HallAdminInline(admin.TabularInline):
    model = Hall


class EventGuideInline(admin.TabularInline):

    model = EventGuide
    form = EventGuideForm
    template = "afisha/admin/event_guide_inline.html"
    ordering = ('-id',)
    readonly_fields = ('source',)
    fieldsets = (
        (None, {
            'fields': ('guide', 'hall', 'source')
        }),
    )

    def hall_set(self):
        return list(Hall.objects.all().values('id', 'name', 'guide_id'))

    def get_queryset(self, request):
        return super(EventGuideInline, self).get_queryset(request).distinct()


class AnnouncementInline(admin.TabularInline):
    """Встраиваемая форма редактирвания анонсов"""

    model = Announcement
    form = AnnouncementAdminInlineForm
    extra = 1


@admin.register(Event)
class EventAdmin(SearchSignalAdminMixin, admin.ModelAdmin):
    inlines = (AnnouncementInline, EventGuideInline, GalleryInline,)
    search_fields = ('title',)
    list_display = ('title', 'buy_btn_clicks', 'is_user_added', 'is_commercial', 'is_hidden')
    list_filter = ('is_user_added', 'is_hidden')
    ordering = ('-id',)
    form = EventForm
    fieldsets = (
        (None, {
            'fields': ('hide_comments', 'type', 'title', 'caption', 'genre', 'age_rating', 'is_hidden', 'prisms')
        }),
        (u'Дополнительно', {
            'classes': ('collapse',),
            'fields': (
                'original_title', 'duration', 'production', 'info', 'content', 'wide_image', 'video',
                'sites', 'premiere_date', 'imdb_id', 'source_url', 'vk_url', 'fb_url', 'ok_url', 'inst_url',
            ),
        }),
        (u'Информация о создании события / (Модерация)', {
            'classes': ('collapse',),
            'fields': ('is_user_added', 'is_commercial', 'get_author_ip', 'created', 'get_info', 'organizer',
                       'organizer_contacts', 'organizer_email', 'get_order_price', 'is_approved', 'get_payment_link'),
        })
    )
    readonly_fields = ('is_user_added', 'get_author_ip', 'created', 'is_commercial', 'organizer',
                       'organizer_contacts', 'get_order_price', 'get_info', 'get_payment_link')

    @admin_media_static
    class Media(object):
        js = ['js/apps-js/admin.js', 'afisha/js/new_admin.js',
              'js/lib/jquery.editable.js', ]

        css = {
            'all': [
                'afisha/css/admin.css',
            ]
        }

    def get_payment_link(self, obj):
        if obj.is_approved:
            return EventOrderHelper(obj).get_invoice_url()
        return ''

    get_payment_link.short_description = u'Ссылка на оплату'

    def get_info(self, obj):
        periods = Period.objects.filter(event_guide__event_id=obj.pk)
        items = []
        for i, period in enumerate(periods, start=1):
            session = Sessions.objects.filter(period=period).first()
            items.append(u'{}) {} {}'.format(i, period.start_date, session.time))
        periods_dates = '\n'.join(items)

        announcements = Announcement.objects.filter(event_id=obj.pk)
        items = []
        for announcement in announcements:
            items.append(u'{}: {} - {}'.format(announcement.get_place_display(), announcement.start, announcement.end))
        announcements_dates = '\n'.join(items)

        info = u'''Тип: {} \n
                   Название: {} \n
                   Описание: {} \n
                   Официальный сайт: {} \n
                   Ссылка на Вконтакте: {} \n
                   Ссылка на Facebook: {} \n
                   Ссылка на Однокласники: {} \n
                   Ссылка на Instagram: {} \n
                   Даты:
                   {} \n
                   Анонсы:
                   {} \n
                   '''.format(obj.type.title, obj.title, obj.content, obj.source_url, obj.vk_url, obj.fb_url,
                              obj.ok_url, obj.inst_url, periods_dates, announcements_dates)
        return info
    get_info.short_description = u'Информация для проверки'

    def get_order_price(self, obj):
        order = EventOrder.objects.filter(event_id=obj.pk).order_by('-pk').first()
        return u'{} руб.'.format(order.price) if order else ''
    get_order_price.short_description = u'Сумма оплаты'

    def get_author_ip(self, obj):
        if not obj.author_ip:
            return ''
        return inttoip(obj.author_ip)
    get_author_ip.short_description = u'IP'

    def save_formset(self, request, form, formset, change):
        with transaction.atomic():
            formset.save()
        if formset.model is EventGuide:
            for form in formset:
                form.save_sessions(form.instance)

            self._update_tickets_sessions(formset.instance)

    def _update_tickets_sessions(self, event):
        """Обновить привязки с сеансами из билетных систем"""

        assert isinstance(event, Event)

        ticket_systems = [
            ('kassy', 'kassyevent_set'),
        ]

        for label, field_name in ticket_systems:
            binder = TicketBinder(label)
            ticket_events = getattr(event, field_name)
            for ticket_event in ticket_events.all():
                binder.update(ticket_event)


class GuideEventGuideInline(EventGuideInline):
    model = EventGuide
    form = GuideEventGuideForm
    formset = PaginatedFormSet
    template = "afisha/admin/guide_event_guide_inline.html"
    fieldsets = (
        (None, {
            'fields': ('event', 'hall')
        }),
    )

    def get_queryset(self, request):
        now = datetime.datetime.now()
        qs = super(GuideEventGuideInline, self).get_queryset(request)
        try:
            is_all_bindings = int(request.GET.get('all', 0))
        except (TypeError, ValueError):
            is_all_bindings = 0

        if is_all_bindings == 0:
            return qs.filter(
                Q(period__end_date__gte=now) | Q(period__isnull=True))\
                .distinct()
        return qs

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(GuideEventGuideInline, self).get_formset(
            request=request,
            obj=obj,
            **kwargs
        )
        try:
            is_all_bindings = int(request.GET.get('all', 0))
        except (TypeError, ValueError):
            is_all_bindings = 0

        setattr(formset, 'is_all_bindings', is_all_bindings)
        setattr(formset, 'page', request.GET.get('page',))
        return formset


@admin.register(Guide)
class GuideAdmin(EventAdmin):
    form = GuideForm
    inlines = (GuideEventGuideInline,)
    fieldsets = None
    list_display = ('__unicode__',)
    list_filter = ()
    search_fields = ('name',)
    readonly_fields = ()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # Вызываем метод от ModelAdmin, а не EventAdmin, чтобы у гида не вызывалось сохранение IMDB рейтинга
        super(EventAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        with transaction.atomic():
            formset.save()
        if formset.model is EventGuide:
            for form in formset:
                form.save_sessions(form.instance)
                try:
                    self._update_tickets_sessions(form.instance.event)
                except ObjectDoesNotExist:
                    pass


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'is_visible')
    list_editable = ('position',)
    ordering = ('position',)


@admin.register(Prism)
class PrismAdmin(admin.ModelAdmin):
    form = PrismAdminForm
    list_display = ('title', 'position', 'is_hidden')
    list_editable = ('position', 'is_hidden')
    exclude = ('svg', )
    ordering = ('position',)

    def save_model(self, request, obj, form, change):
        if 'icon' in form.changed_data:
            obj.svg = form.cleaned_data.get('icon').read()

        super(PrismAdmin, self).save_model(request, obj, form, change)


@admin.register(Review)
class ReviewAdmin(news_admin.ArticleAdmin):
    form = ReviewAdminForm
    list_display = news_admin.ArticleAdmin.list_display + ('related_event',)
    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic', ),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_super', 'is_announce'),
        }),
        (u'Категории', {
            'fields': ('event', 'sites', ('subject', 'subject_main'), 'type', 'project')
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_image', 'social_text', 'social_label', 'social_card'),
        }),
        (None, {
            'fields': ('stamp', 'published_time', 'slug', 'title', 'caption', 'content', 'author', 'image',
                       'tags'),
        }),
    )

    def related_event(self, obj):
        return unicode(obj.event)
    related_event.short_description = u'Событие'


@admin.register(Article)
class ArticleAdmin(news_admin.ArticleAdmin):
    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic', ),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_super', 'is_advertising', 'is_announce', 'hide_comments', 'disable_comments'),
        }),
        (u'Категории', {
            'fields': ('sites', 'category', ('subject', 'subject_main'), 'type', 'project', 'template')
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
            'fields': ('stamp', 'published_time', 'slug', 'title', 'caption', 'content', 'author', 'image',
                       'header_image', 'image_label', 'tags'),
        }),
    )


@admin.register(Photo)
class PhotoAdmin(news_admin.PhotoAdmin):
    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
                ('scroll_depth_statistic', ),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_super', 'is_advertising', 'is_announce'),
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
            'fields': ('stamp', 'published_time', 'slug', 'title', 'caption', 'caption_short', 'share_text', 'content',
                       'author', 'image', 'tags'),
        }),
    )


@admin.register(Poll)
class PollAdmin(polls_admin.PollAdmin, news_admin.SectionMaterialAdmin):
    pass


@admin.register(Test)
class TestAdmin(testing_admin.TestAdmin, news_admin.SectionMaterialAdmin):
    pass


@admin.register(AnnouncementColor)
class AnnouncementColorAdmin(admin.ModelAdmin):
    list_display = ('number', 'value', 'position')
    list_editable = ('value', 'position',)
    ordering = ('position',)

    def number(self, obj):
        return u'Цвет №%s' % obj.pk


class EventBindListFilter(admin.SimpleListFilter):
    """Фильтрация в админке по признаку прявязано или нет событие"""

    title = u'есть привязка'
    parameter_name = 'event_bind'

    def lookups(self, request, model_admin):
        return (
            ('yes', u'да'),
            ('no', u'нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(event__isnull=False)

        if self.value() == 'no':
            return queryset.filter(event__isnull=True)

###############################################################################
# Админские классы для билетных систем
###############################################################################


class TicketBaseAdminMixin(admin.ModelAdmin):
    """Базовый класс для админок моделей из билетных систем"""

    change_list_form = None

    @admin_media_static
    class Media(object):
        css = {
            'all': ('css/admin.css', ),
        }
        js = (
            'js/apps-js/admin.js',
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_changelist_form(self, request, **kwargs):
        if self.change_list_form:
            return self.change_list_form
        else:
            return super(TicketBaseAdminMixin, self).get_changelist_form(request, **kwargs)


class TicketBuildingAdmin(TicketBaseAdminMixin):
    list_display_links = None
    list_editable = ['guide']
    change_list_form = TicketBuildingChangeListAdminForm


class TicketHallAdmin(TicketBaseAdminMixin):
    list_display_links = None
    list_editable = ['hall']
    change_list_form = TicketHallChangeListAdminForm


class TicketEventAdmin(TicketBaseAdminMixin):
    list_display_links = None
    list_select_related = False
    list_filter = [EventBindListFilter]
    list_editable = ['event']
    date_hierarchy = 'date_start'
    change_list_form = TicketEventChangeListAdminForm

    def get_queryset(self, request):
        qs = super(TicketEventAdmin, self).get_queryset(request)
        # Отображаем только активные события (у которых есть сеансы в будущем)
        return qs.active()

    def save_model(self, request, obj, form, change):
        obj.save()

        if 'event' in form.changed_data:
            if obj.event:
                # Связывание сеансов для наших событий
                bind_ticket_sessions.delay(obj.ticket_label, obj.id)
            else:
                # Отвязывание сеансов от наших событий
                unbind_ticket_sessions.delay(obj.ticket_label, obj.id)

    @options(short_description=u'Ближайший сеанс')
    def nearest_session_date(self, obj):
        """Дата ближайшего сеанса"""

        if not obj.nearest_session:
            return u''

        return u'{0:%H:%M %d.%m.%y}'.format(obj.nearest_session.show_datetime)


@admin.register(KassyBuilding)
class KassyBuildingAdmin(TicketBuildingAdmin):
    list_display = ['title', 'address', 'guide']


@admin.register(KassyEvent)
class KassyEventAdmin(TicketEventAdmin):
    list_display = ['title', 'nearest_session_date', 'nearest_session_building', 'rollerman',
                    'nearest_session_link', 'event']
    search_fields = ['title']

    @options(short_description=u'Ссылка', allow_tags=True)
    def nearest_session_link(self, obj):
        """Ссылка ближайшего сеанса на сайте kassy.ru"""

        if not obj.nearest_session:
            return u''

        return mark_safe(u'<a href="{}/" target="_blank">посмотреть на kassy.ru</a>'.format(
            obj.nearest_session.get_absolute_url())
        )

    @options(short_description=u'Место ближайшего сеанса')
    def nearest_session_building(self, obj):
        """Место ближайшего сеанса"""

        if not obj.nearest_session:
            return u''

        try:
            building = obj.nearest_session.hall.building
        except ObjectDoesNotExist:
            return u''
        else:
            return u'{}'.format(building)

    @options(short_description=u'Организатор')
    def rollerman(self, obj):
        """Организатор события"""

        if not obj.kassy_rollerman_id:
            return u'нет данных'

        kassy_rollerman = KassyRollerman.objects.filter(id=obj.kassy_rollerman_id).first()

        return u'{}'.format(kassy_rollerman or '')


@admin.register(RamblerHall)
class RamblerHallAdmin(TicketHallAdmin):
    list_display = ['building', 'name', 'hall']
    list_editable = ['hall']
    ordering = ['building', 'name']


@admin.register(RamblerEvent)
class RamblerEventAdmin(TicketEventAdmin):
    list_display = ['name', 'original_name', 'year', 'genre', 'nearest_session_date', 'event']
    search_fields = ['name', 'original_name']


# @admin.register(KinomaxHall)
class KinomaxHallAdmin(TicketHallAdmin):
    list_display = ['building', 'title', 'hall']
    ordering = ['building', 'title']


# @admin.register(KinomaxEvent)
class KinomaxEventAdmin(TicketEventAdmin):
    list_display = ['title', 'nearest_session_date', 'original_link', 'event']
    search_fields = ['title']

    @options(short_description=u'Ссылка', allow_tags=True)
    def original_link(self, obj):
        """Ссылка ближайшего сеанса на сайте kinomax"""

        if not obj.nearest_session:
            return u''

        return mark_safe(u'<a href="https://kinomax.ru/films/{}" target="_blank">посмотреть на kinomax</a>'.format(
            obj.id)
        )
