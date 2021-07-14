# -*- coding: utf-8 -*-

import json
import operator

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.utils import unquote, get_deleted_objects
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.core.urlresolvers import reverse
from django.db import connection, transaction, models
from django.db import router
from django.db.models.query_utils import Q
from django.db.models.signals import pre_delete, post_delete
from django.http import HttpResponseBadRequest, HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from irk.afisha.admin import HallAdminInline
from irk.afisha.forms import GuideAdminForm
from irk.afisha.models import Guide
from irk.gallery.admin import GalleryBBCodeInline
from irk.map.models import MapHouse
from irk.obed.forms import EstablishmentAdminForm
from irk.obed.models import Establishment
from irk.phones.forms import AddressAdminInlineForm, AddressFormset, SectionAdminForm, FirmAdminForm, \
    SectionFirmAdminForm
from irk.phones.helpers import firms_library
from irk.phones.models import Address, Firms as Firm, Sections as Section, MetaSection
from irk.tourism.forms.firm import TourBaseAdminForm, HotelAdminForm, TourFirmAdminForm
from irk.tourism.models import Hotel, TourBase, TourFirm
from irk.utils.files.admin import admin_media_static
from irk.utils.search.helpers import SearchSignalAdminMixin


class AddressInline(admin.StackedInline):
    model = Address
    formset = AddressFormset
    form = AddressAdminInlineForm
    extra = 0


class FirmsAdmin(SearchSignalAdminMixin, admin.ModelAdmin):
    inlines = (AddressInline, GalleryBBCodeInline)
    form = FirmAdminForm
    search_fields = ('name', 'user__username', 'alternative_name')
    list_display = ('name', 'visible', 'display_user')
    list_select_related = True
    list_editable = ('visible',)
    list_filter = ('visible',)
    ordering = ('-id',)

    @admin_media_static
    class Media(object):
        css = {
            'all': ('phones/css/admin.firms.css',),
        }
        js = (
            'js/lib/jquery-1.7.2.min.js',
            'js/apps-js/plugins.js',
            'phones/js/admin.firms.js',
        )

    def display_user(self, obj):
        if not obj.user_id:
            return u''
        return obj.user.username

    display_user.short_description = u'Пользователь'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        # Для наследованных объектов подрисовываем кнопки, чтобы из админки
        # фирмы можно было перейти на форму наследованной фирмы
        extendable_objects = []
        for model in firms_library:
            try:
                extended_obj = model.objects.get(pk=object_id)
            except ObjectDoesNotExist:

                info = self.model._meta.app_label, self.model._meta.object_name.lower()

                extendable_objects.append({
                    'title': model._meta.verbose_name,
                    'url': '%s?from=%s' % (
                        reverse('admin:%s_%s_add' % (model._meta.app_label, model._meta.object_name.lower())),
                        object_id
                    ),
                })
            else:
                extendable_objects.append({
                    'title': model._meta.verbose_name,
                    'url': reverse('admin:phones_%s_change' % extended_obj._meta.object_name.lower(),
                                   args=[extended_obj.pk, ]),
                    'selected': True
                })

        extra_context['extendable_objects'] = extendable_objects

        return super(FirmsAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        return [url(r'^unlinked-with-map/$', self.admin_site.admin_view(self._unmapped)),
                url(r'^unlinked-with-map/(?P<address_id>\d+)/$',
                    self.admin_site.admin_view(self._link_address)),
                url(r'^with-blank-addresses/', self.admin_site.admin_view(self._blank_addresses)),
                ] + super(FirmsAdmin, self).get_urls()

    def _unmapped(self, request):
        """Фирмы, которые невозможно найти на карте"""

        query = '''SELECT firm.id, firm.name, street.name, adr.id, city.name, adr.location,
            (SELECT COUNT(*) FROM map_houses WHERE map_houses.street_id = street.id AND map_houses.name = adr.location) AS map_houses
            FROM `phones_address` AS adr
            LEFT JOIN `streets_main` AS street ON adr.streetID = street.id
            LEFT JOIN `phones_firms` AS firm ON adr.firm_id = firm.id
            LEFT JOIN `cities` AS city ON adr.city_id = city.id
            WHERE firm.visible = 1 %(where)s
            GROUP BY adr.streetID, adr.location
            HAVING map_houses = 0
            ORDER BY firm.name
        '''

        q = request.GET.get('q')
        if q:
            data = {'where': 'AND firm.name LIKE "%%%%%s%%%%"' % q}
        else:
            data = {'where': ''}

        query = query % data

        try:
            page = int(request.GET.get('page'))
        except (TypeError, ValueError):
            page = 1

        cursor = connection.cursor()

        cursor.execute(query)
        objects = cursor.fetchall()

        paginate = Paginator(objects, 25)
        try:
            objects = paginate.page(page)
        except (EmptyPage, InvalidPage):
            objects = paginate.page(1)

        return render(request, 'phones/admin/lost_firms.html',
                      {'objects': objects, 'page': page, 'q': q})

    def _blank_addresses(self, request):
        """Фирмы, у которых адрес заполнен не полностью"""

        query = '''SELECT firm.id, firm.name, street.name, adr.streetID, adr.location, city.name
            FROM `phones_address` AS adr
            LEFT JOIN `streets_main` AS street ON adr.streetID = street.id
            LEFT JOIN `phones_firms` AS firm ON adr.firm_id = firm.id
            LEFT JOIN `cities` AS city ON adr.city_id = city.id
            WHERE adr.streetID IS NULL OR adr.streetID = 0 OR adr.location = ''
            ORDER BY firm.name
        '''

        cursor = connection.cursor()

        cursor.execute(query)
        objects = cursor.fetchall()

        try:
            page = int(request.GET.get('page'))
        except (TypeError, ValueError):
            page = 1

        paginate = Paginator(objects, 25)
        try:
            objects = paginate.page(page)
        except (EmptyPage, InvalidPage):
            objects = paginate.page(1)

        return render(request, 'phones/admin/blank_addresses.html',
                      {'objects': objects, 'page': page})

    @csrf_exempt
    def _link_address(self, request, address_id):
        """Привязка адреса к карте"""

        address = get_object_or_404(Address, pk=address_id)
        if request.POST:

            type_ = request.POST.get('type')
            if not type_ in ('draw', 'link'):
                return HttpResponseBadRequest()

            if type_ == 'link':
                house_id = request.POST.get('house')
                house = get_object_or_404(MapHouse, pk=house_id)

                address.location = house.name
                address.streetid = house.street
                address.save()
            else:
                points = json.loads(request.POST.get('points'))
                points.append(points[0])  # Должна быть замкнутая линия
                points = [(x[1], x[0]) for x in points]
                multipolygon = MultiPolygon((Polygon(points),))

                house = MapHouse(street=address.streetid, name=address.location,
                                 center=multipolygon.centroid, poly=multipolygon)
                house.save()

            return HttpResponse('ok')

        return render(request, 'phones/admin/link_address.html',
                      {'address': address, 'key': settings.GOOGLE_MAPS_KEY})


class MetaSectionAdmin(admin.ModelAdmin):
    ordering = ('-id',)


def name(obj):
    diff = "&nbsp;&nbsp;&nbsp;&nbsp;".join(['' for i in range(1, obj.level * 2 - 1)])

    return '%s%s' % (diff, obj.name)


name.short_description = "Название"
name.allow_tags = True


def firms_count(obj):
    ct = ContentType.objects.get_for_model(obj)
    # TODO: перенести эту строку в шаблон
    return u"""
        <div style='width:30px;float:left;font-size:12px;padding-top:7px;'>%s</div> <nobr><input type="text" callback="ObjectAutocompleteCallback" autocomplete="off" name="object_name" style='width:320px;' url="/utils/objects/%s/" class="autocomplete_input ac_input" id="id_object_name"><button class='goto_button' from='%s'>></button></nobr>
    """ % (unicode(obj.org_count), ct.pk, obj.pk)


firms_count.short_description = "Фирмы"
firms_count.allow_tags = True

ERROR__SECTIONS_VAR = 'error_sections'


class ErrorSectionsFilter():

    def choices(self, cl):
        return [
            {'display': 'Да', 'query_string': '?%s=1' % ERROR__SECTIONS_VAR, 'selected': cl.error_rubrics},
            {'display': 'Нет', 'query_string': '?%s=0' % ERROR__SECTIONS_VAR, 'selected': not cl.error_rubrics}
        ]

    def title(self):
        return 'ошибочным рубрикам'


class SectionInline(admin.StackedInline):
    model = Section
    extra = 0
    verbose_name_plural = u'Подрубрики'


class SectionErrorFilter(admin.SimpleListFilter):
    title = u'ошибочным рубрикам'
    parameter_name = 'error_sections'

    def lookups(self, request, model_admin):
        return (
            ('1', u'Да'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            # todo: no_phones_map
            # TODO: писать понятные TODO
            error_sections = queryset.filter(map__pk__gt=0).extra(where=['(`rght` - `lft` > 1)']).distinct()
            if error_sections.count():
                queryset = queryset.filter(reduce(operator.or_, [Q(lft__range=rng) | Q(lft__lt=rng[0], rght__gt=rng[0])
                                                                 for rng in error_sections.values_list('lft', 'rght')]))
            else:
                queryset = queryset.filter(id=None)

        return queryset


class SectionAdmin(admin.ModelAdmin):
    """Админ рубрик"""

    list_display = (name, 'name_short', 'is_guide', 'position', 'content_type', firms_count, 'level')
    search_fields = ('name', 'name_short')
    list_editable = ('is_guide', 'position')
    ordering = ('lft',)
    list_filter = (SectionErrorFilter, 'is_guide')
    inlines = (SectionInline,)
    form = SectionAdminForm
    save_as = True

    @admin_media_static
    class Media(object):
        js = (
            'js/lib/jquery-ui.js',
            'js/apps-js/plugins.js',
            'phones/js/admin.js',
        )
        css = {
            'all': (
                'css/jquery-ui.css',
                'css/admin.css',
            ),
        }

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.object_name.lower()

        return [
                   url(r'^move/$', self.admin_site.admin_view(self.move), name='%s_%s_move' % info),
               ] + super(SectionAdmin, self).get_urls()

    def move(self, request):
        """Перемещение фирм из одной рубрики в другую"""

        from_obj = get_object_or_404(Section, pk=request.GET.get('from'))
        to_obj = get_object_or_404(Section, pk=int(request.GET.get('to')))
        # todo: no_phones_map
        for item in from_obj.map_set.exclude(firm__id__in=to_obj.map_set.all().values_list('firm', flat=True)):
            item.section = to_obj
            item.save()

        from_obj.org_count = 0
        from_obj.save()

        return HttpResponse('ok')


admin.site.register(MetaSection, MetaSectionAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Firm, FirmsAdmin)


class ScanStoreAdmin(admin.ModelAdmin):
    list_display = ('ownership', 'cuption', 'type', 'data_formated', 'url09', 'firm_edit')
    list_filter = ('type',)
    list_display_links = ('cuption',)
    search_fields = ('cuption', 'data')


class GisFirm(Firm):
    class Meta:
        db_table = Firm._meta.db_table
        proxy = True
        verbose_name = u'Граббер фирм'
        verbose_name_plural = u'Граббер фирм'


# Для контентных моделей-наследников фирм делаем прокси модели и регистрируем их в админке телефонов


class SectionFirmAdmin(FirmsAdmin):
    """Базовый админ для всех контентных моделей фирм"""

    change_form_template = 'admin/phones/firms/change_form.html'
    form = SectionFirmAdminForm

    def save_model(self, request, obj, form, change):
        if not change and form.cleaned_data.get('firms_ptr'):
            # При добавлении контентной модели ставим у нее firms_ptr на оригинальную фирму, чтобы сохранить старый id
            obj.pk = form.cleaned_data['firms_ptr'].pk

        obj.save()

    def get_changeform_initial_data(self, request):
        initial = super(SectionFirmAdmin, self).get_changeform_initial_data(request)

        if 'from' in request.GET:
            firm = Firm.objects.get(pk=request.GET.get('from'))
            initial['firms_ptr'] = firm.pk
            for field in FirmAdminForm.Meta.fields:
                value = getattr(firm, field)
                if isinstance(value, models.Manager):
                    initial[field] = ','.join([str(x) for x in value.all().values_list('id', flat=True)])
                elif isinstance(value, models.Model):
                    initial[field] = value.pk
                else:
                    initial[field] = value

        return initial

    def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
        if 'from' in request.GET:
            return []

        return super(SectionFirmAdmin, self).get_inline_formsets(request, formsets, inline_instances, obj)

    def _create_formsets(self, request, obj, change):
        if 'from' in request.GET:
            return [], []
        return super(SectionFirmAdmin, self)._create_formsets(request, obj, change)

    @csrf_protect_m
    @transaction.atomic
    def delete_view(self, request, object_id, extra_context=None):
        """The 'delete' admin view for this model."""

        opts = self.model._meta
        app_label = opts.app_label

        obj = self.get_object(request, unquote(object_id))

        if not self.has_delete_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') %
                          {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        using = router.db_for_write(self.model)

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (deleted_objects, perms_needed, protected) = get_deleted_objects(
            [obj], opts, request.user, self.admin_site, using)

        # При проверке разрешения на удаление наследуемой модели используется метод `get_delete_permission`
        # от класса `Option`, а не `has_delete_permission` админа модели. Из-за этого проверяется разрешение
        # не `delete_firms`, а например `delete_employerproxy`.
        # Так как мы не можем в данный момент перегрузить этот метод, чтобы правильно определить разрешение, перегружаем
        # весь `delete_view` и избавляемся от проверки разрешений.
        # Соответствующий тикет django: https://code.djangoproject.com/ticket/18096
        perms_needed = None

        if request.POST:  # The user has already confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj_display = force_unicode(obj)
            self.log_deletion(request, obj, obj_display)
            self.delete_model(request, obj)

            self.message_user(request, _('The %(name)s "%(obj)s" was deleted successfully.') %
                              {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj_display)})

            if not self.has_change_permission(request, None):
                return HttpResponseRedirect(reverse('admin:index',
                                                    current_app=self.admin_site.name))
            return HttpResponseRedirect(reverse('admin:%s_%s_changelist' %
                                                (opts.app_label, opts.object_name.lower()),
                                                current_app=self.admin_site.name))

        object_name = force_unicode(opts.verbose_name)

        if perms_needed or protected:
            title = _("Cannot delete %(name)s") % {"name": object_name}
        else:
            title = _("Are you sure?")

        context = {
            "title": title,
            "object_name": object_name,
            "object": obj,
            "deleted_objects": deleted_objects,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": opts,
            "app_label": app_label,
        }
        context.update(extra_context or {})

        return TemplateResponse(request, self.delete_confirmation_template or [
            "admin/%s/%s/delete_confirmation.html" % (app_label, opts.object_name.lower()),
            "admin/%s/delete_confirmation.html" % app_label,
            "admin/delete_confirmation.html"
        ], context, current_app=self.admin_site.name)

    def history_view(self, request, object_id, extra_context=None):
        """"The 'history' admin view for this model."""

        from django.contrib.admin.models import LogEntry
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        action_list = LogEntry.objects.filter(
            object_id=object_id,
            content_type__id__exact=ContentType.objects.get_for_model(model).id
        ).select_related().order_by('action_time')
        # If no history was found, see whether this object even exists.
        obj = get_object_or_404(model, pk=unquote(object_id))
        context = {
            'title': _('Change history: %s') % force_unicode(obj),
            'action_list': action_list,
            'module_name': capfirst(force_unicode(opts.verbose_name_plural)),
            'object': obj,
            'app_label': app_label,
            'opts': opts,
        }
        context.update(extra_context or {})
        return TemplateResponse(request, self.object_history_template or [
            "admin/%s/%s/object_history.html" % (app_label, opts.object_name.lower()),
            "admin/%s/object_history.html" % app_label,
            "admin/object_history.html"
        ], context, current_app=self.admin_site.name)

    def additional_formset_data(self, firm):
        """Для дополнительных данных к формсету"""

        return {}

    def delete_model(self, request, obj):
        ct = ContentType.objects.get_for_model(obj)
        obj_cls = ct.model_class()

        pre_delete.send(sender=obj_cls, instance=obj)
        connection.cursor().execute('DELETE FROM `%s` WHERE firms_ptr_id = %s' % (obj._meta.db_table, obj.pk))
        post_delete.send(sender=obj_cls, instance=obj)

    def has_add_permission(self, request):
        return request.user.has_perm('phones.change_firms')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('phones.change_firms')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('phones.change_firms')


class GuideProxy(Guide):
    class Meta:
        proxy = True
        verbose_name = u'Гид'
        verbose_name_plural = u'Гид'


class GuideAdmin(SectionFirmAdmin):
    form = GuideAdminForm
    inlines = FirmsAdmin.inlines + (HallAdminInline,)
    search_fields = FirmsAdmin.search_fields + ('title_short',)

    def additional_formset_data(self, firm):
        return {
            'hall_set-TOTAL_FORMS': 0,
            'hall_set-INITIAL_FORMS': 0,
            'hall_set-MAX_NUM_FORMS': None,
        }


admin.site.register(GuideProxy, GuideAdmin)


class HotelProxy(Hotel):
    class Meta:
        proxy = True
        verbose_name = u'Гостиница'
        verbose_name_plural = u'Туризм: Гостиницы'


class HotelAdmin(SectionFirmAdmin):
    form = HotelAdminForm


admin.site.register(HotelProxy, HotelAdmin)


class TourBaseProxy(TourBase):
    class Meta:
        proxy = True
        verbose_name = u'Турбаза'
        verbose_name_plural = u'Туризм: Турбазы'


class TourBaseAdmin(SectionFirmAdmin):
    form = TourBaseAdminForm


admin.site.register(TourBaseProxy, TourBaseAdmin)


class TourFirmProxy(TourFirm):
    class Meta:
        proxy = True
        verbose_name = u'Турфирма'
        verbose_name_plural = u'Туризм: Турфирмы'


class TourFirmAdmin(SectionFirmAdmin):
    form = TourFirmAdminForm


admin.site.register(TourFirmProxy, TourFirmAdmin)


class EstablishmentProxy(Establishment):
    class Meta:
        proxy = True
        verbose_name = u'Обед: Заведение'
        verbose_name_plural = u'Обед: Заведения'


class EstablishmentAdmin(SectionFirmAdmin):
    list_filter = ('visible', 'is_new', 'summer_terrace')
    form = EstablishmentAdminForm
    fieldsets = (
        (None, {
            'fields': ['hide_comments', 'disable_comments', 'user', 'name', 'alternative_name', 'visible', 'is_new',
                       'url', 'mail', 'section', 'main_section', 'description', 'logo', 'guru_cause', 'types',
                       'contacts', 'parking', 'facecontrol', 'bill', 'card_image', 'virtual_tour', 'firms_ptr']
        }),
        (u'Характеристики', {
            'fields': ['wifi', 'dancing', 'karaoke', 'children_room', 'terrace', 'catering', 'cooking_class',
                       'breakfast', 'children_menu', 'cashless', 'live_music', 'entertainment', 'banquet_hall']
        }),
        (u'Бизнес-ланч', {
            'classes': ('collapse',),
            'fields': ['business_lunch', 'business_lunch_price', 'business_lunch_time']
        }),
        (u'Новогодние корпоративы', {
            'classes': ('collapse',),
            'fields': ['corporative', 'corporative_guest', 'corporative_price', 'corporative_description']
        }),
        (u'Барофест', {
            'classes': ('collapse',),
            'fields': ['barofest_description']
        }),
        (u'Летние веранды', {
            'classes': ('collapse',),
            'fields': ['summer_terrace', 'summer_terrace_description']
        }),
        (u'Доставки', {
            'classes': ('collapse',),
            'fields': ['delivery', 'delivery_description', 'delivery_districts', 'delivery_price_free']
        }),
        (u'Дополнительные поля для гастрономической карты', {
            'fields': ['point', 'type_name', 'type_name_en', 'name_en', 'address_name_en'],
        }),
    )


admin.site.register(EstablishmentProxy, EstablishmentAdmin)
