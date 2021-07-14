import datetime
import operator
from itertools import chain
from functools import reduce

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import (IncorrectLookupParameters,
                                          update_wrapper)
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse

from invoice.models import Invoice
from options.models import Site
from utils.decorators import options
from utils.files.admin import admin_media_static
from utils.http import JsonResponse
from . import models
from .forms import (BannerAdminForm, ClientForm, CommunicationAdminForm,
                    FileAdminInlineForm, FileTestForm,
                    PeriodAdminInlineForm, UserOptionForm)
from .helpers import banner_duplicate, file_get_info, add_utm
from .models import (Booking, BookingHistory, ClientType, Communication,
                     CommunicationHistory, Contact, Limit,
                     MailHistory, ManagerClientHistory, Targetix,
                     UserOption)
from .order_helpers import AdvOrderHelper


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'pk', 'visible', 'booking_visible', 'targetix')
    list_editable = ('visible', 'booking_visible')
    list_filter = ('visible', 'booking_visible', 'site')
    ordering = ('-id',)
    search_fields = ('name',)

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.object_name.lower()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        return [url(r'^(?P<object_id>\d+)/change/check/$', self.check_place, name='%s_%s_check' % info), ] \
               + super(PlaceAdmin, self).get_urls()

    def check_place(self, request, object_id):
        """Проверка, что место в данный момент не занято"""

        now = datetime.datetime.now()

        place = get_object_or_404(models.Place, pk=object_id)
        periods = models.Period.objects.filter(date_from__lte=now, date_to__gte=now,
                                               banner__places=place).select_related('banner', 'banner__client')

        if len(periods):
            result = u'<p>На этом месте уже находятся баннеры:</p>'
            for period in periods:
                result += u'<p><a href="%(url)s">%(banner)s</a> (%(client)s)</p>' % {
                    'banner': period.banner.name,
                    'client': period.banner.client.name,
                    'url': reverse('admin:adv_banner_change', args=(period.banner_id,))
                }
            return JsonResponse({'length': len(periods), 'text': result})

        return JsonResponse({'length': 0})


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active', 'is_deleted')
    search_fields = ('name',)
    form = ClientForm


class PeriodInline(admin.TabularInline):
    model = models.Period
    form = PeriodAdminInlineForm
    extra = 1


class FileInline(admin.StackedInline):
    model = models.File
    extra = 1
    form = FileAdminInlineForm
    fields = (
        'main', 'html5', 'main_768', 'main_420', 'main_320', 'dummy', 'video', 'video_webm', 'show_player',
        'url', 'alt', 'text', 'deleted'
    )

    def get_queryset(self, request):
        queryset = super(FileInline, self).get_queryset(request)
        queryset = queryset.filter(deleted=False)
        return queryset

    def has_delete_permission(self, request, obj=None):
        return False


class LimitInline(admin.TabularInline):
    model = Limit
    fields = ('is_active', 'view_limit', 'view_left', 'updated', 'enabled', 'auto_disabled')
    readonly_fields = ('view_left', 'updated', 'enabled', 'auto_disabled')


def banner_field(name, title):
    def cell(object, context=None):
        context = {
            'object': object,
            'name': name,
            'context': context,
        }
        return render_to_string('admin/adv/banner/%s.html' % name, context)

    cell.short_description = title
    cell.allow_tags = True

    return cell


class BannerSiteFilter(admin.SimpleListFilter):
    title = u'Раздел'
    parameter_name = 'site'

    def lookups(self, request, model_admin):
        sites = map(list, Site.objects.filter(booking_visible=True).values_list('slugs', 'name'))
        for site in sites:
            if site[0] == 'home':
                site[1] = u'Главная'
        return sites

    def queryset(self, request, queryset):
        value = self.value()

        if value:
            site = get_object_or_404(Site, slugs=value)
            queryset = queryset.filter(places__site=site)

        return queryset


class BannerAdmin(admin.ModelAdmin):
    inlines = (LimitInline, FileInline, PeriodInline)
    list_select_related = True
    list_filter = (BannerSiteFilter,)
    list_display = (
        banner_field('name', u'Название'),
        banner_field('client', u'Клиент'),
        banner_field('periods', u'Период размещения'),
        'list_places', 'invoice', 'is_payed', 'limit_views'
    )
    search_fields = ('name', 'client__name', 'places__name')
    form = BannerAdminForm
    ordering = ('-id',)
    fieldsets = (
        (None, {
            'fields': ('name', 'url', 'alt', 'bgcolor', 'width', 'height', 'places', 'client', 'invoice', 'is_payed',
                       'is_alternate_external'),
        }),
        (u'Мониторинг кликов', {
            'classes': ('collapse',),
            'fields': ('click_monitor', 'click_count'),
        }),
        (u'Дополнительно', {
            'classes': ('collapse',),
            'fields': ('pixel_audit', 'iframe'),
        }),
    )
    readonly_fields = ('click_count',)

    @admin_media_static
    class Media(object):
        js = (
            'js/apps-js/admin.js',
            'adv/js/admin.js',
        )
        css = {
            'all': ('css/jquery-ui.css', 'adv/css/admin.css'),
        }

    def limit_views(self, obj):
        limit = obj.limit if hasattr(obj, 'limit') else False
        text = _boolean_icon(limit.is_active if limit else False)
        if limit:
            text = u'{} Осталось: {} из {}'.format(text, limit.view_left, limit.view_limit)
        return text

    limit_views.short_description = u'Ограничение просмотров'
    limit_views.allow_tags = True

    def list_places(self, obj):
        places = obj.places.all()
        if len(places) > 0:
            return '<ul><li>%s</li></ul>' % '</li><li>'.join([x.name for x in obj.places.all()])
        return ''

    list_places.short_description = u'Места'
    list_places.allow_tags = True

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.object_name.lower()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        return [url(r'^(.+)/duplicate/$', wrap(self.duplicate), name='%s_%s_duplicate' % info), ] \
               + super(BannerAdmin, self).get_urls()

    def duplicate(self, request, object_id):
        """Дублирование баннера"""

        banner = get_object_or_404(models.Banner, pk=object_id)
        new_banner = banner_duplicate(banner)

        return HttpResponseRedirect(reverse('admin:adv_banner_change', args=[new_banner.pk]))

    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """

        qs = self.model._default_manager.get_queryset()

        if hasattr(request, 'date_range'):
            start_date, end_date = request.date_range
            if start_date and end_date:
                qs = qs.filter(
                    Q(period__date_from__range=(start_date, end_date)) | \
                    Q(period__date_to__range=(start_date, end_date)) | \
                    Q(period__date_from__lt=start_date, period__date_to__gt=end_date)
                ).distinct()
            else:
                # Баннеры без периодов размещения
                qs = self.model._default_manager.exclude(pk__in=models.Period.objects.all().values('banner_id'))

        ordering = self.ordering or ()  # otherwise we might try to *None, which is bad ;)
        # Reversing the search queryset
        if not ordering and 'q' in request.GET:
            ordering = ('-pk',)
        if ordering:
            qs = qs.order_by(*ordering)

        return qs

    def changelist_view(self, request, extra_context=None):
        """Даты нет - текущий день
        Выбран месяц - все за месяц"""

        date = request.GET.get('date')
        params = dict(request.GET.items())

        search = request.GET.get('q')
        client = request.GET.get('client__exact')
        site = request.GET.get('site', '')
        extra_context = {'q': search}
        if not search and not client:
            if not date:
                # Не указана дата, показываем за текущий день
                now = datetime.datetime.now()

                return HttpResponseRedirect('?date=%4d-%02d-%02d&site=%s' % (now.year, now.month, now.day, site))
            else:
                if date == '0':
                    # Показываем баннеры, у которых нет периодов размещения
                    start_date = end_date = None
                    date_type = 0
                else:
                    # Баннеры за определенный период размещения
                    date_type = len(date.split('-'))
                    if date_type == 2:
                        # Показываем баннеры за месяц
                        try:
                            start_date = datetime.datetime.strptime(date + '-01', '%Y-%m-%d')
                        except ValueError:
                            return HttpResponse('.')

                        if start_date.month < 12:
                            end_date = start_date.replace(month=start_date.month + 1) - datetime.timedelta(days=1)
                        else:
                            end_date = start_date.replace(day=31)

                    elif date_type == 3:
                        # Показываем баннеры за день
                        start_date = end_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                    else:
                        # Ввели ерунду, показываем за текущий день
                        start_date = end_date = datetime.datetime.now()

                setattr(request, 'date_range', (start_date, end_date))
                del params['date']

            qdict = QueryDict('')
            qdict = qdict.copy()
            qdict.update(params)

            request.GET = qdict

            extra_context = {'date': start_date, 'date_type': date_type}

        client = request.GET.get('client__exact')
        if client:
            try:
                extra_context['client'] = models.Client.objects.get(pk=client)
            except models.Client.DoesNotExist:
                pass

        for param in self.list_display:
            if callable(param) and param.func_name == 'cell':
                param.func_defaults = (extra_context,)

        return super(BannerAdmin, self).changelist_view(request, extra_context)

    def save_formset(self, request, form, formset, change):
        formset.save()
        # @todo : Переделать, возможно show_time должны различаться у разных периодов
        # Для того чтобы у периодов всегда show_time
        # соответствовал банеру
        for form in formset:
            # Не пересохраняем периоды, которые должны быть удалены
            deleted = form.cleaned_data.get('DELETE') is True

            if not deleted and isinstance(form.instance, models.Period) and form.instance.date_from:
                form.instance.show_time_start = form.instance.banner.show_time_start
                form.instance.show_time_end = form.instance.banner.show_time_end
                form.instance.save()

    def _add_utm(self, banner):
        if banner.url is not None and 'utm_source' not in banner.url and banner.url.strip():
            before = banner.url
            after = banner.url = add_utm(banner.url, banner)
            return before != after

        return False

    def save_model(self, request, obj, form, change):
        super(BannerAdmin, self).save_model(request, obj, form, change)

        if self._add_utm(obj):
            obj.save(update_fields=['url'])
            messages.add_message(request, messages.INFO, u'В ссылку баннера добавлены UTM-метки')


class LogItog(object):
    data = None

    def __init__(self, *args, **kwargs):
        self.data = kwargs

    def __getattr__(self, name):
        return ''


class LogAdmin(admin.ModelAdmin):
    list_display = ('get_date', 'views', 'clicks', 'scrolls', 'ctr')
    date_hierarchy = 'date'

    actions_on_top = False
    actions = False

    @options(short_description=u'Дата')
    def get_date(self, obj):
        return obj.date.strftime('%d.%m.%Y')

    @options(short_description=u'Количество просмотров')
    def views(self, obj):
        return obj.cnt_views

    @options(short_description=u'Количество переходов')
    def clicks(self, obj):
        return obj.cnt_clicks

    @options(short_description=u'Количество доскролов')
    def scrolls(self, obj):
        return obj.cnt_scrolls

    @options(short_description=u'CTR')
    def ctr(self, obj):
        if obj.cnt_views:
            ctr = float(obj.cnt_clicks) / obj.cnt_views * 100
            return "%.02f%%" % ctr
        return 0

    def changelist_view(self, request, extra_context=None):
        from django.contrib.admin.views.main import ChangeList, ERROR_FLAG

        if not self.has_change_permission(request):
            raise PermissionDenied()

        # Remove action checkboxes if there aren't any actions available.
        list_display = list(self.list_display)

        try:
            cl = ChangeList(
                request, self.model, list_display, self.list_display_links, self.list_filter, self.date_hierarchy,
                self.search_fields, self.list_select_related, self.list_per_page, self.list_max_show_all,
                self.list_editable, self
            )
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render(request, 'admin/invalid_setup.html', {'title': 'Database error'})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        banner_pk = request.GET.get('banner__id__exact')
        banner = get_object_or_404(models.Banner, pk=banner_pk)

        file_pk = request.GET.get('file__id__exact')
        on_file = models.File.objects.filter(pk=file_pk).first() if file_pk else None

        data = {}
        date_filter = []
        for period in banner.period_set.all():
            date_filter.append(Q(date__range=(period.date_from, period.date_to)))

        queryset = cl.get_queryset(request)
        if date_filter:
            queryset = queryset.filter(reduce(operator.or_, date_filter))
        queryset = queryset.values('date').distinct()

        views = queryset.filter(action=models.Log.ACTION_VIEW).annotate(views=Sum('cnt'))
        clicks = queryset.filter(action=models.Log.ACTION_CLICK).annotate(clicks=Sum('cnt'))
        scrolls = queryset.filter(action=models.Log.ACTION_SCROLL).annotate(scrolls=Sum('cnt'))

        for line in chain(views, clicks, scrolls):
            day = line['date']
            views = line.get('views') or 0
            clicks = line.get('clicks') or 0
            scrolls = line.get('scrolls') or 0

            if day not in data:
                log = models.Log(date=day)
                log.cnt_views = log.cnt_clicks = log.cnt_scrolls = 0
                data[day] = log

            data[day].cnt_views += views
            data[day].cnt_clicks += clicks
            data[day].cnt_scrolls += scrolls

        cl.formset = None

        if self.list_editable:
            FormSet = self.get_changelist_formset(request)
            cl.formset = FormSet(queryset=cl.result_list)

        cl.list_display_links = ['None']
        cl.result_list = [data[x] for x in sorted(data.keys())]
        itog = {'views': 0, 'clicks': 0, 'scrolls': 0}
        for row in cl.result_list:
            itog['views'] += row.cnt_views
            itog['clicks'] += row.cnt_clicks
            itog['scrolls'] += row.cnt_scrolls

        if itog['views']:
            ctr = float(itog['clicks']) / itog['views'] * 100
            itog['ctr'] = "%.02f%%" % ctr
        else:
            itog['ctr'] = 0

        try:
            banner.file_set.order_by("id")[0].dummy.open()
            dummy = banner.file_set.order_by("id")[0].dummy
        except Exception:
            dummy = None
        context = {
            'title': u'%s | Статистика' % banner, 'cl': cl, 'itog': itog, 'dummy': dummy, 'banner': banner,
            'on_file': on_file
        }
        return super(LogAdmin, self).changelist_view(request, context)


class FileAdmin(admin.ModelAdmin):
    """Проверка параметров файлов"""

    change_list_template = 'admin/adv/file_test.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': u'Информация о файле'}
        if request.POST:
            form = FileTestForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                f = open("%s/%s" % (settings.MEDIA_ROOT, "img/tmp/%s" % file.name), "w")
                f.write(file.read())
                f.close()
                extra_context['file'] = f
                extra_context['file_name'] = file.old_name
                extra_context['info'] = file_get_info(file)
        else:
            form = FileTestForm()
        extra_context['form'] = form

        return super(FileAdmin, self).changelist_view(request, extra_context)


class MailHistoryAdmin(admin.ModelAdmin):
    list_display = ('manager', 'date', 'title', 'text')


class UserOptionAdmin(admin.ModelAdmin):
    form = UserOptionForm


class CommunicationAdmin(admin.ModelAdmin):
    form = CommunicationAdminForm


class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'place', 'from_date', 'to_date', 'deleted')
    search_fields = ('client__name', 'place__name', 'comment')
    list_editable = ('deleted',)
    ordering = ('-id',)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'email', 'phone',)
    search_fields = ('name', 'client__name', 'email', 'phone')
    list_filter = ('primary_contact',)
    ordering = ('-id',)


class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'date_of_action', 'booking',)
    search_fields = ('user__username', 'action__action',)
    ordering = ('-id',)


class CommunicationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'date_of_action', 'communication',)
    search_fields = ('user__username', 'action__action',)
    ordering = ('-id',)


class ManagerClientHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'date_of_action', 'client',)
    search_fields = ('user__username', 'action__action', 'client__name')
    ordering = ('-id',)


class TargetixAdmin(admin.ModelAdmin):
    pass


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


class AdvOrderAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'service', 'created', 'get_is_payed')
    readonly_fields = ('user', 'price', 'created', 'updated', 'description',
                       'client_name', 'client_contacts', 'service', 'get_payment_link', 'get_is_payed')
    exclude = ('invoice',)

    def get_payment_link(self, obj):
        if obj.status == models.AdvOrder.STATUS_APPROVED:
            return AdvOrderHelper(obj).get_invoice_url()
        return ''

    get_payment_link.short_description = u'Ссылка на оплату'

    def get_is_payed(self, obj):
        invoice = obj.invoice
        if invoice and invoice.status == Invoice.STATUS.SUCCESS:
            return 'Оплачено'
        return 'Не оплачено'

    get_is_payed.short_description = u'Статус оплаты'


admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingHistory, BookingHistoryAdmin)
admin.site.register(ClientType)
admin.site.register(Communication, CommunicationAdmin)
admin.site.register(CommunicationHistory, CommunicationHistoryAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(MailHistory, MailHistoryAdmin)
admin.site.register(ManagerClientHistory, ManagerClientHistoryAdmin)
admin.site.register(models.Agent)
admin.site.register(models.Banner, BannerAdmin)
admin.site.register(models.Log, LogAdmin)
admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.File, FileAdmin)
admin.site.register(models.Location)
admin.site.register(models.Net)
admin.site.register(models.Place, PlaceAdmin)
admin.site.register(Targetix, TargetixAdmin)
admin.site.register(UserOption, UserOptionAdmin)
admin.site.register(models.Service, ServiceAdmin)
admin.site.register(models.AdvOrder, AdvOrderAdmin)
