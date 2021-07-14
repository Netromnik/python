# -*- coding: utf-8 -*-

import calendar
import datetime
import logging
from collections import OrderedDict

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy

from irk.afisha.models import Guide, CurrentSession
from irk.afisha.views.base import AfishaMixin
from irk.afisha.views.events import EventList
from irk.afisha.views.filters import date_filter, guide_filter, is_3d_filter
from irk.map.models import Cities as City
from irk.obed.models import Establishment
from irk.phones.models import Sections as Section, Address
from irk.phones.permissions import is_moderator
from irk.phones.views.base.list import ListFirmBaseView
from irk.phones.views.base.read import ReadFirmBaseView
from irk.utils.helpers import int_or_none
from irk.utils.http import JsonResponse
from irk.utils.user_options import City as CityOption


logger = logging.getLogger(__name__)


class ListFirmView(ListFirmBaseView):
    """Список фирм рубрики гида"""

    template = 'guide/index.html'
    ajax_template = 'guide/place_list.html'
    model = Guide

    # Количество объектов на странице
    page_limit_default = 20
    # Максимальное количество объектов на странице
    page_limit_max = page_limit_default

    def get(self, request, **kwargs):

        # Параметры пагинации
        start_index = int_or_none(self.request.GET.get('start')) or 0
        self.start_index = max(start_index, 0)
        page_limit = int_or_none(self.request.GET.get('limit')) or self.page_limit_default
        self.page_limit = min(page_limit, self.page_limit_max)

        # Получение текущей рубрики
        rub = self.kwargs.get('rub')
        if rub:
            params = {}
            try:
                params['pk'] = int(rub)
            except (ValueError, TypeError):
                params['slug'] = rub
            section = get_object_or_404(Section, is_guide=True, **params)
        else:
            section = Section.objects.filter(is_guide=True, on_guide_index=True).first()

        queryset = self.get_queryset(section)
        object_list, page_info = self._paginate(queryset)

        firms_arr = []
        firms = list(object_list)
        city = CityOption(request).value
        addresses = list(Address.objects.filter(city_id=city, firm_id__in=[x.pk for x in firms])
                         .select_related('streetid'))

        for address in addresses:
            address.city_id = city

        for firm in firms:
            firm_addresses = [x for x in addresses if x.firm_id_id == firm.pk]
            if not firm_addresses:
                continue

            firms_arr.append((firm, firm_addresses))

        context = {
            'firms_arr': firms_arr,
            'sections': Section.objects.filter(is_guide=True).order_by('position'),
            'section': section,
            'curr_rub': section.pk if section else None,
        }

        if self.request.is_ajax():
            return self._render_ajax_response(context, page_info)

        context.update(page_info)
        return render(request, self.template, context)

    def get_queryset(self, section, **kwargs):
        city = City.objects.get(alias='irkutsk')
        queryset = Guide.objects.filter(section=section, address__city_id=city, visible=True) \
            .distinct().order_by('name').select_related('firms_ptr')
        return queryset

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

    def _paginate(self, queryset):
        """
        Разбить queryset на страницы.

        :param QuerySet queryset: результирующий набор данных
        :return: список объектов на странице и информация о странице
        :rtype: tuple
        """
        object_count = queryset.count()

        end_index = self.start_index + self.page_limit
        end_index = min(end_index, object_count)
        object_list = queryset[self.start_index:end_index]

        page_info = {
            'has_next': object_count > end_index,
            'next_start_index': end_index,
            'next_limit': min(self.page_limit_default, object_count - end_index)
        }

        return object_list, page_info


class ReadCinemaMixin(object):
    """ Страница кинотеатра т.к. кино очень отличается от всего остального """

    def get_cinema_context(self, obj, sessions_qs, date):
        """ Для кино по умолчанию возврашаем обычное расписание
            с делением по дням, но если указан GET параметр `show_by_halls`
            возвращает список залов с проходящими в них событиями
        """

        if not self.request.GET.get('show_by_halls', False):
            result = self.get_extra_context(obj, sessions_qs, date)
            result.update({
                'any_2d': sessions_qs.filter(is_3d=False, time__isnull=False).exists(),
                'any_3d': sessions_qs.filter(is_3d=True).exists(),
            })

            return result

        halls = OrderedDict()
        for session in sessions_qs.select_related("event", "hall", "period").order_by('real_date'):
            if not session.hall:
                continue

            if not session.hall in halls:
                halls[session.hall] = {}

            if not session.event in halls[session.hall]:
                halls[session.hall][session.event] = {
                    'first_session': session.real_date,
                    'sessions': [],
                }

            if session.time is not None:
                halls[session.hall][session.event]['sessions'].append(session)
        for hall, events in halls.items():
            halls[hall] = sorted(events.items(), key=lambda i: i[1]['first_session'])

        return {
            'schedule': sorted(halls.items(), key=lambda h: h[0].position),
            'by_hall': True,  # Флаг для того, чтобы не рендерить дату в заголовке
            'any_2d': sessions_qs.filter(is_3d=False, time__isnull=False).exists(),
            'any_3d': sessions_qs.filter(is_3d=True).exists(),
        }


class ReadNightMixin(object):

    def get_night_context(self, obj, sessions_qs, date):
        return {
            'schedule': EventList(self, sessions_qs)[:]
        }


class ReadExhibitionsMixin(object):

    def get_exhibitions_context(self, obj, sessions_qs, date):
        sessions = list(sessions_qs.select_related('event'))

        schedule = []
        for event in set(x.event for x in sessions):
            first_date = sorted((x.real_date for x in sessions if x.event == event))[0]
            last_date = sorted((x.real_date for x in sessions if x.event == event), reverse=True)[0]
            setattr(event, 'price', sorted(x.period.price for x in sessions if x.event == event)[0])
            schedule.append((event, first_date, last_date))

        return {
            'schedule': schedule,
        }


class ReadFirmView(AfishaMixin, ReadCinemaMixin, ReadNightMixin, ReadExhibitionsMixin, ReadFirmBaseView):
    model = Guide
    template_name = 'guide/place.html'
    filters = [date_filter, guide_filter, is_3d_filter, guide_filter]
    show_month = True
    sessions_order = 'real_date'
    redirect_url = reverse_lazy('afisha:index')

    def get(self, request, **kwargs):
        """Перегружаем GET метод, чтобы выбирать,
           в какой шаблон будем рендерить данные

           Расписания выводятся в разном формате и с разными пагинаторами
           по дням
        """
        today = datetime.date.today()
        self.obj = self.get_object(request, kwargs)

        if isinstance(self.obj, HttpResponse):
            return self.obj

        self.event_type = self.obj.event_type if self.obj.event_type_id else None
        self.event_type_name = self.event_type.alias if self.event_type else ''

        self.date = self.get_date(request, **kwargs)

        if not self.date:
            try:
                self.date = datetime.datetime.strptime(request.GET.get('date'), '%Y%m%d').date()
            except (ValueError, TypeError):
                self.date = datetime.date.today()

        if self.date < datetime.date.today() and self.event_type.hide_past:
            logger.debug('Past dates are disallowed. Raising 404 now')
            raise Http404()

        # Корректируем дату на ближайшую, на которую есть сеансы
        try:
            self.date = CurrentSession.objects.filter(
                date__gte=self.date, is_hidden=False, guide=self.obj).values_list('date', flat=True).order_by('date')[0]
        except IndexError:
            pass

        # Есть ли у заведения или одного из залов заведения схема зала
        has_map = self.obj.map or self.obj.hall_set.filter(map__isnull=False).exists()

        data = self.get_data()
        self.sessions = self.get_sessions(self.get_filters(data))
        context = {
            'object': self.obj,
            'comments': bool(request.GET.get('comments', False)),
            'review': bool(request.GET.get('review', False)),
            'map': bool(request.GET.get('map', False)),
            'has_map': has_map,
            'moderator': is_moderator(request.user),
            'filters': dict([(f.param, f) for f in self.filters]),
            'view': self,
            'data': data,
            'current_date': self.date,
            'today': today,
        }

        # if not context.get('comments'):
        if hasattr(self, "get_%s_context" % self.event_type_name):
            context.update(getattr(self, "get_%s_context" % self.event_type_name)(self.obj, self.sessions, self.date))
        else:
            context.update(self.get_extra_context(self.obj, self.sessions, self.date))

        templates = self.get_template_names(event_type=self.event_type_name)

        return render(request, templates, context)

    def get_data(self):
        # По умалчанию для всех типов заведений
        # кроме кинотеатров выбрано
        data = {'guide': self.obj}
        if self.event_type_name == 'cinema':
            data['date'] = self.date
        elif self.event_type_name in ('night', 'exhibitions'):
            data['date'] = '30day'
        elif self.request.GET.get('month') or self.show_month:
            data['date'] = ('month', self.date)
        elif not self.request.GET.get('full'):
            data['date'] = self.date
        return data

    def get_extra_context(self, obj, sessions_qs, date):
        """ Возвращает события с группировакой по дням """

        schedule = {}
        for session in sessions_qs.select_related("event"):
            if not session.date in schedule:
                schedule[session.date] = {}
            if not session.event in schedule[session.date]:
                schedule[session.date][session.event] = {
                    'sessions': [],
                    'first_session': session.real_date,
                    'date': session.date,
                    'hall': session.hall,
                }
            if session.time is not None:
                schedule[session.date][session.event]['sessions'].append(session)

        for date, events in schedule.items():
            schedule[date] = sorted(events.items(), key=lambda i: i[1]['first_session'])
            for event, data in events.items():
                setattr(event, 'schedule', [data])
        return {
            'schedule': sorted(schedule.items(), key=lambda i: i[0]),
        }

    def get_object(self, request, extra_params):
        now = datetime.datetime.now()
        obj = super(ReadFirmView, self).get_object(request, extra_params)

        establishment_ct = ContentType.objects.get_for_model(Establishment)

        if isinstance(obj, Establishment) and not obj.currentsession_set.filter(real_date__gte=now).exists() and\
                obj.section.filter(content_type=establishment_ct).exists():
            try:
                return redirect(Establishment.objects.get(pk=obj.pk).get_absolute_url())
            except Establishment.DoesNotExist:
                pass

        return obj


class AjaxCalendarView(ReadFirmView):
    """ Ajax пагинатор по датам
        учитывает выбранные фильтры: тап события, заведение
        GET параметр month=201301
    """

    def get_extra_context(self, obj, sessions_qs, date):
        for flt in self.filters:
            if flt.param == 'date':
                choices = flt.get_choices(self)
                break
        else:
            return {}
        month = self.request.GET.get('month')
        current = choices['calendar'][0].replace(day=1)

        if month:
            try:
                current = datetime.datetime.strptime(month, "%Y%m").date()
            except ValueError:
                pass

        month_days = calendar.monthrange(current.year, current.month)[1]
        last = current.replace(day=month_days)
        next_date = next((date for date in choices['calendar'] if date > last), None)
        prev_date = next((date for date in reversed(choices['calendar']) if date < current), None)

        c = calendar.Calendar()
        return {
            'current': current,
            'calendar': c.monthdatescalendar(current.year, current.month),
            'active_dates': choices['calendar'],
            'next_date': next_date,
            'prev_date': prev_date,
        }


read = ReadFirmView.as_view(template_name=['guide/%(event_type)s/place.html', 'guide/place.html'])

sessions = ReadFirmView.as_view(template_name=['guide/%(event_type)s/sessions.html', 'guide/sessions.html'],
                                show_month=False)

calendar_paginator = AjaxCalendarView.as_view(
    template_name=['afisha/tags/calendar-paginator.html'])

rubric = ListFirmView.as_view()
