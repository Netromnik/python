# -*- coding: utf-8 -*-

import datetime
import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, render, redirect
from django.template.loader import render_to_string

from irk.afisha.models import CurrentSession
from irk.gallery.forms.helpers import gallery_formset
from irk.obed.forms import EstablishmentForm, EstablishmentSearchForm
from irk.obed.models import Establishment, Article, Menu, Poll
from irk.obed.permissions import can_edit_establishment, is_moderator, get_moderators
from irk.options.models import Site
from irk.phones.forms import AddressObedFormSet
from irk.phones.models import Sections
from irk.phones.views.base.create import CreateFirmBaseView
from irk.phones.views.base.list import ListFirmBaseView
from irk.phones.views.base.read import ReadFirmBaseView
from irk.phones.views.base.update import UpdateFirmBaseView
from irk.utils import settings as utils_settings
from irk.utils.fields.helpers import field_verbose_name
from irk.utils.helpers import int_or_none
from irk.utils.http import JsonResponse
from irk.utils.notifications import tpl_notify


class ListFirmView(ListFirmBaseView):
    """Список фирм рубрики"""

    model = Establishment
    template = 'obed/establishment/index.html'
    ajax_template = 'obed/establishment/list.html'
    # Количество объектов на странице
    page_limit_default = 24
    # Максимальное количество объектов на странице
    page_limit_max = page_limit_default

    def get(self, request, **kwargs):
        self._parse_params()

        queryset = self.get_queryset()
        queryset = self._filter(queryset)
        queryset = self._sort(queryset)
        object_list, page_info = self._paginate(queryset)

        context = {
            'object_list': object_list,
            # Особая обработка для страницы бизнес-ланча. Меняется карточка заведения.
            'business_lunch_page': self.business_lunch_page,
        }

        if self.request.is_ajax():
            return self._render_ajax_response(context, page_info)

        context.update({
            'current_section': self.section,
            'total_object_count': queryset.count(),
            'sorting_urls': self._sorting_urls(),
            'sorting': self.sorting,
        })
        context.update(page_info)

        return render(request, self.template, context)

    def _parse_params(self):
        """Разобрать параметры переданные в url и в строке запроса"""

        self.section = None
        if self.kwargs.get('section_slug'):
            self.section = get_object_or_404(Sections, slug=self.kwargs['section_slug'])

        # Параметры пагинации
        start_index = int_or_none(self.request.GET.get('start')) or 0
        self.start_index = max(start_index, 0)
        page_limit = int_or_none(self.request.GET.get('limit')) or self.page_limit_default
        self.page_limit = min(page_limit, self.page_limit_max)

        # Параметры сортировки
        self.sorting = self.request.GET.get('sort', 'name')

        # Страница бизнес-ланча
        self.business_lunch_page = self.request.GET.get('business_lunch', False)

        # Параметры фильтра
        self.filters = {}
        form = EstablishmentSearchForm(self.request.GET, initial=self.request.GET)
        if form.is_valid():
            self.filters = dict((k, v) for k, v in form.cleaned_data.iteritems() if v)

    def get_queryset(self, **kwargs):
        queryset = self.model.objects.filter(is_active=True, visible=True).prefetch_related('firms_ptr').distinct()

        if self.section:
            queryset = queryset.filter(section=self.section)

        if not self.show_hidden(self.request):
            queryset = queryset.filter(visible=True)

        return queryset

    def _filter(self, queryset):
        """
        Применить фильтры.

        :return: отфильтрованный queryset
        """

        queryset = self._filter_by_worktime(queryset)
        queryset = self._filter_by_bill(queryset)
        queryset = self._filter_by_dinner(queryset)

        if self.filters:
            queryset = queryset.filter(**self.filters)

        return queryset

    def _filter_by_worktime(self, queryset):
        """Отфильтровать по времени работы"""

        work_24_hour = self.filters.pop('work_24_hour', None)
        open_2_hour = self.filters.pop('open_2_hour', None)

        if work_24_hour and not open_2_hour:
            queryset = queryset.filter(address__twenty_four_hour=True)
        elif open_2_hour:
            # TODO протестировать производительность
            extra_hours = 60 * 60 * 2  # Количество секунд в 2х часах

            dtime = datetime.datetime.now()
            stamp = dtime.weekday() * 60 * 60 * 24 + dtime.hour * 60 * 60 + dtime.minute * 60

            q_objects = Q(address__twenty_four_hour=True)

            q_objects |= Q(address__address_worktimes__start_stamp__lte=stamp,
                           address__address_worktimes__end_stamp__gte=stamp + extra_hours)

            # Если ПН то проверить время работы в ВС
            if dtime.weekday() == 0:
                extra_stamp = stamp + 60 * 60 * 24 * 7  # Количество секунд в неделе
                q_objects |= Q(address__address_worktimes__weekday=utils_settings.WEEKDAY_SUN,
                               address__address_worktimes__end_stamp__gte=extra_stamp + extra_hours)

            queryset = queryset.filter(q_objects)

        return queryset

    def _filter_by_bill(self, queryset):
        """Отфильтровать по среднему счету"""

        bill_list = self.filters.pop('bill', [])

        if bill_list:
            q_objects = Q()
            for bill in bill_list:
                q_objects |= Q(bill=bill)
                # В форме варианты 500-1000 и 1000-1500 объединины в одну кнопку 1500.
                if int(bill) == Establishment.BILL_1000_1500:
                    q_objects |= Q(bill=Establishment.BILL_500_1000)
            queryset = queryset.filter(q_objects)

        return queryset

    def _filter_by_dinner(self, queryset):
        """Отфильтровать по ужину"""

        is_dinner = self.filters.pop('dinner', None)

        if is_dinner:
            queryset = queryset.filter(gurucause__is_dinner=True)

        return queryset

    def _sort(self, queryset):
        """
        Отсортировать queryset

        :rtype: QuerySet
        """

        if self.sorting == 'business_lunch':
            return queryset.order_by('business_lunch_price')
        else:
            return queryset.order_by('name')

    def _paginate(self, queryset):
        """
        Разбить queryset на страницы.

        :param QuerySet queryset: результирующий набор данных
        :return: список объектов на странице и информация о странице
        :rtype: tuple
        """
        object_count = queryset.count()

        if self.request.is_ajax():
            end_index = self.start_index + self.page_limit
            end_index = min(end_index, object_count)
            object_list = queryset[self.start_index:end_index]
        else:
            end_index = self.page_limit - 1
            object_list = queryset[:end_index]

        page_info = {
            'has_next': object_count > end_index,
            'next_start_index': end_index,
            'next_limit': min(self.page_limit_default, object_count - end_index),
            'page_limit': self.page_limit,
        }

        return object_list, page_info

    def _render_ajax_response(self, context, page_info):
        """
        Отправить ответ на Ajax запрос

        :param dict context: контекст шаблона
        :param dict page_info: информация о странице
        """

        return JsonResponse(dict(
            html=render_to_string(self.ajax_template, context),
            **page_info
        ))

    def _sorting_urls(self):
        """
        Сформировать и вернуть список urls для сортировки

        :rtype: dict
        """
        params = self.request.GET.copy()
        # Удаляем параметр sort, если он есть
        params.pop('sort', None)
        params_encoded = u'&{}'.format(params.urlencode()) if params else ''

        return {
            'name': '{}?sort=name{}'.format(self.request.path, params_encoded),
            'business_lunch': '{}?sort=business_lunch{}'.format(self.request.path, params_encoded),
        }


section_list = ListFirmView.as_view()


class ReadFirmView(ReadFirmBaseView):
    """Просмотр заведения"""

    model = Establishment
    template = 'obed/establishment/read.html'
    redirect_url = reverse_lazy('obed:index')

    def extra_context(self, request, obj, extra_params=None):
        user_is_moderator = is_moderator(request.user)
        can_edit = can_edit_establishment(request.user, obj)

        current_section = get_object_or_404(Sections, slug=extra_params['section_slug'])

        # Проверка привязана ли рубрика к заведению
        try:
            obj.section.get(pk=current_section.pk)
        except Sections.DoesNotExist:
            raise Http404

        # Упоминания
        mentions = Article.objects.filter(mentions=obj, is_hidden=False).select_subclasses('obed_review')

        # Формируем список адресов из поля url, т.к иногда в нем содержатся несколько адресов.
        obj.url_list = obj.url.split()

        context = {
            'can_edit': can_edit,
            'user_is_moderator': user_is_moderator,
            'establishment': obj,
            'mentions': mentions,
            'current_section': current_section,
            'latest_poll': self._get_latest_poll(),
            'tags': self._get_tags(obj),
        }
        context.update(self._get_tabs_info(obj))

        return context

    def _get_tabs_info(self, establishment):
        """
        :param Establishment establishment: объект заведения
        :return: Информация об имеющихся для заведения вкладках и текущей вкладке
        :rtype: dict
        """

        has_gallery = bool(establishment.gallery.main_gallery())
        has_menu = Menu.objects.filter(establishment=establishment).exists()
        has_about = bool(establishment.description or establishment.facecontrol or establishment.parking)
        # Пока 3D тур выключен для всех
        has_tour = bool(establishment.virtual_tour)
        has_events = CurrentSession.objects \
            .filter(real_date__gt=datetime.datetime.now(), guide_id=establishment.id, is_hidden=False) \
            .exists()
        # TODO: определять наличие отзывов для заведения
        has_comments = True
        has_corporative = establishment.corporative and bool(establishment.corporative_description)
        has_summer_terrace = establishment.summer_terrace and bool(establishment.summer_terrace_description)
        has_barofest = establishment.barofest and bool(establishment.barofest_description)
        has_delivery = establishment.delivery and bool(establishment.delivery_description)

        tab = self.request.GET.get('tab', None)
        if tab and vars().get('has_{}'.format(tab)):
            current_tab = tab
        elif has_gallery:
            current_tab = 'gallery'
        elif has_about:
            current_tab = 'about'
        else:
            current_tab = 'comments'

        return {
            'has_gallery': has_gallery,
            'has_menu': has_menu,
            'has_about': has_about,
            'has_tour': has_tour,
            'has_events': has_events,
            'has_comments': has_comments,
            'has_corporative': has_corporative,
            'has_summer_terrace': has_summer_terrace,
            'has_delivery': has_delivery,
            'has_barofest': has_barofest,
            'current_tab': current_tab,
        }

    def _get_latest_poll(self):
        """Получить последнее голосование"""

        today = datetime.date.today()

        site = Site.objects.get(slugs='obed')
        poll = Poll.material_objects.for_site(site) \
            .filter(start__lte=today, end__gte=today) \
            .order_by('-stamp', '-published_time') \
            .last()

        return poll

    def _get_tags(self, establishment):
        """Получить теги"""

        possible_tags = [
            'breakfast', 'business_lunch', 'wifi', 'dancing', 'banquet_hall', 'terrace',
            'children_room', 'children_menu', 'karaoke', 'live_music', 'entertainment',
            'cooking_class', 'catering'
        ]

        base_url = reverse('obed:list')

        tags = []
        for tag in possible_tags:
            if getattr(establishment, tag, False):
                tags.append({
                    'name': field_verbose_name(establishment, tag),
                    'link': u'{}?{}=on'.format(base_url, tag),
                })

        return tags


read = ReadFirmView.as_view()


class CreateFirmView(CreateFirmBaseView):
    """Создание фирмы"""

    model = Establishment
    template = 'obed/establishment/add.html'
    form = EstablishmentForm
    address_form = AddressObedFormSet

    def notifications(self, request, obj, extra_context=None):
        tpl_notify(u'Добавлена новая организация на obed', 'obed/notif/new_establishment.html', {'establishment': obj},
                   request, emails=get_moderators().values_list('email', flat=True))

    def response_completed(self, request, obj):
        context = {}
        return render(request, 'obed/establishment/added.html', context)

    def save_model(self, request, obj, form):
        obj.save()

    def get_gallery_form(self, request, obj=None):
        return gallery_formset(self.request.POST, self.request.FILES, instance=self.model(), user=self.request.user)

    def get_form_initial_data(self, request, obj=None, extra_context=None):
        return {'bill': Establishment.BILL_0_500}

add = CreateFirmView.as_view()


class UpdateFirmView(UpdateFirmBaseView):
    """Редактирование фирмы"""

    model = Establishment
    template = 'obed/establishment/edit.html'
    form = EstablishmentForm
    address_form = AddressObedFormSet

    def notifications(self, request, obj, extra_context=None):
        super(UpdateFirmView, self).notifications(request, obj, extra_context)
        emails = get_moderators().values_list('email', flat=True)
        tpl_notify(u'Добавлена новая организация в разделе «Обед»', 'obed/notif/edit_establishment.html',
                   {'establishment': obj}, request, emails=emails)

    def get_object(self, request, extra_params):

        try:
            obj = self.model.objects.get(pk=extra_params['firm_id'])
        except ObjectDoesNotExist:
            obj = get_object_or_404(self.model, old_establishment_id=extra_params['firm_id'])
        self.user = obj.user

        if not can_edit_establishment(request.user, obj):
            return HttpResponseForbidden()

        return obj

    def save_model(self, request, obj, form):
        # TODO: Должно сохраняться автоматически
        obj.types.through.objects.filter(establishment=obj, ).delete()
        for type_item in form.cleaned_data.get("types"):
            obj.types.through.objects.create(establishment=obj, type=type_item)
        obj.section.through.objects.filter(firms=obj, ).delete()
        for section in form.cleaned_data.get("section"):
            obj.section.through.objects.create(firms=obj, sections=section)
        obj.save()

    def get_gallery_form(self, request, obj=None):
        return gallery_formset(self.request.POST, self.request.FILES, instance=obj,
                               user=self.user if self.user else self.request.user)

    def response_completed(self, request, obj):
        return redirect(".")

edit = UpdateFirmView.as_view()


def delete(request, establishment_id):
    """Удаление заведения"""

    if not is_moderator(request.user):
        return HttpResponseForbidden()
    try:
        establishment = Establishment.objects.get(id=establishment_id)
    except ObjectDoesNotExist:
        establishment = get_object_or_404(Establishment, old_establishment_id=establishment_id)

    establishment.visible = False
    establishment.save()

    # Пересчет счетчиков
    for type_ in establishment.types.all():
        type_.recalculate_firms_count()

    for section in establishment.section.all():
        section.recalculate_firms_count()
        section.save()

    return HttpResponseRedirect(reverse('obed:index'))


def tab_content(request, firm_id, tab_name):
    """Содержимое вкладок на странице заведения"""

    est = get_object_or_404(Establishment, pk=firm_id, visible=True)

    if tab_name == 'events':
        announcements = CurrentSession.objects \
            .filter(real_date__gt=datetime.datetime.now(), guide_id=est.id, is_hidden=False) \
            .order_by('date', 'time')
        context = {
            'announcements': announcements
        }
    elif tab_name == 'menu':
        if hasattr(est, 'establishment_menu'):
            context = {'menu': est.establishment_menu}
        else:
            raise Http404
    elif tab_name == 'comments':
        context = {'obj': est}
    else:
        raise Http404

    template = 'obed/establishment/read_ajax_{}.html'.format(tab_name)
    return render(request, template, context)


def direct_redirect(request, firm_id):
    """Редирект со старых прямых ссылок на заведения без указания рубрики"""

    est = get_object_or_404(Establishment, pk=firm_id, visible=True)
    return redirect(est.get_absolute_url(), permanent=True)
