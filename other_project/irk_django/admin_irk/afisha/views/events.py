# -*- coding: utf-8 -*-

import calendar
import datetime
from copy import deepcopy
from itertools import groupby
from math import ceil
from operator import itemgetter

from django.core.paginator import EmptyPage, InvalidPage, Page, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.views.generic.base import TemplateView

from irk.afisha.controllers import ExtraCinemaController, ExtraCultureController
from irk.afisha.models import CurrentSession, Event, EventType, Prism
from irk.afisha.settings import DEFAULT_EXTRA_AJAX_COUNT
from irk.afisha.templatetags.afisha_tags import cinema_ajax_calendar_paginator
from irk.afisha.views.base import AfishaMixin
from irk.afisha.views.filters import (
    date_filter, event_filter, genre_filter, guide_filter, is_3d_filter, prism_filter, time_filter, type_filter
)
from irk.utils.helpers import int_or_none
from irk.utils.http import json_response


class EventList(object):
    """ Список событий
        т.к. используя денормализованную таблицу, нет возможности
        использовать пагинатор напрямую
    """

    db_fields = ["time", "date", "event_id", "guide_id"]

    def __init__(self, view, sessions):
        self.view = view
        self.sessions = sessions
        self.keys = []

        # Для списка реализуем `values_list`, чтобы получить на выходе одну и ту же структуру
        if isinstance(self.sessions, list):
            self.query = [tuple([getattr(session, field) for field in self.db_fields]) for session in self.sessions]
        else:
            self.query = self.sessions.order_by('real_date').values_list(*self.db_fields)

    def __getitem__(self, key):
        if type(key) is slice:
            now = datetime.datetime.now()
            items = list(self.query)
            objects = list(map(itemgetter(0), groupby(items)))

            # Удаление дублирующихся
            seen = set()
            seen_add = seen.add
            objects = [x for x in objects if x not in seen and not seen_add(x)]

            objects = objects[key]
            objects = [dict(zip(self.db_fields, o)) for o in objects]

            # Т.к. привязки к гиду может и не быть
            guides_filter = Q(guide_id__in=set([o['guide_id'] for o in objects if o['guide_id']]))
            if any([o for o in objects if not o['guide_id']]):
                guides_filter = guides_filter | Q(guide_id__isnull=True)

            # выборка все сеансов на текущей странице с событиями
            sessions = CurrentSession.objects.filter(
                date__in=set([o['date'] for o in objects]),
                event_id__in=set([o['event_id'] for o in objects]),
                end_date__gte=now,
                is_hidden=False,
            ).filter(guides_filter).select_related('event', 'period').prefetch_related('event__type',
                                                                                       'event__genre').order_by(
                "real_date")

            events = []
            for item in objects:
                event = self.create_event(
                    [session for session in sessions if session.date == item['date'] and
                     session.time == item['time'] and
                     session.guide_id == item['guide_id'] and
                     session.event_id == item['event_id']]
                )
                if event:
                    events.append(event)

            return sorted(events, key=lambda x: x.schedule.first.fake_date)

    def __len__(self):
        return len(self.query)

    def create_event(self, sessions):
        """ Возвращает событие с расписанием на основе сеансов """
        if sessions:
            session = sessions[0]
            event = deepcopy(session.event)
            event.schedule.append(session)
            for s in sessions[1:]:
                event.schedule.append(s)

            return event


class PaginatorSplitDate(Paginator):
    """
    Разделение событий по датам.
    Для элементов списка событий в афише определяет первый элемент для каждой новой даты и добавляет атрибут
    split_date содержащий эту дату. Не добавляет split_date  для первой даты.

    Дополнительный параметр first_page_count позволяет задать произвольное количество элементов на первой странице
    """

    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, first_page_count=None):
        super(PaginatorSplitDate, self).__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.first_page_count = first_page_count
        self.first_page_offset = per_page - first_page_count if first_page_count else 0

    def page(self, number):
        number = self.validate_number(number)

        if number == 1 and self.first_page_count:
            self.per_page = self.first_page_count

        bottom = (number - 1) * self.per_page

        if number > 1:
            bottom -= self.first_page_offset

        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count

        split_date_prev = None
        if bottom > 0:
            split_date_prev = self.object_list[bottom - 1:bottom][0].schedule.first.date

        events = self.object_list[bottom:top]
        for key, event in enumerate(events):
            split_date_current = events[key].schedule.first.date
            if split_date_prev and split_date_current != split_date_prev:
                events[key].split_date = split_date_current
            split_date_prev = split_date_current

        return Page(events, number, self)

    @cached_property
    def num_pages(self):
        """
        Returns the total number of pages.
        """
        if self.count == 0 and not self.allow_empty_first_page:
            return 0
        hits = max(1, self.count - self.orphans + self.first_page_offset)
        return int(ceil(hits / float(self.per_page)))


class EventsListView(AfishaMixin, TemplateView):
    """ Список событий: Главная + индексы разделов
    """

    index_types = EventType.objects.filter(on_index=True)  # TODO: вынести в __init__ класса
    event_type = None
    prism = None
    show_prism_paginator = False

    page_kwarg = 'page'
    paginate_by = 16
    paginator_class = PaginatorSplitDate

    filters = [date_filter, time_filter, type_filter, genre_filter, guide_filter,
               is_3d_filter, event_filter, prism_filter]

    def get(self, request, *args, **kwargs):
        self.event_type = self.get_event_type(request, *args, **kwargs)
        self.event_type_name = self.event_type.alias if self.event_type else ''

        self.current_date = self.get_date(request, *args, **kwargs)
        self.sessions = self.get_sessions(self.get_filters())

        return super(EventsListView, self).get(request, *args, **kwargs)

    def get_filter_data(self):
        """ Возвращает данные для фильтров
        """
        data = {
            'date': self.current_date,
        }

        # На главной афиши по-умолчанию выбираем дефолтную призму
        if self.event_type is None:
            try:
                data['prism'] = Prism.objects.visible()[0].pk
            except IndexError:
                pass

        return data

    def get_data(self):
        data = self.get_filter_data()
        self.prism = data.get('prism')
        # Для призм выводим все события
        if self.prism:
            self.index_types = EventType.objects.all()
        return data

    def paginate(self, objects):
        page_kwarg = self.page_kwarg
        page = self.request.GET.get(page_kwarg) or 1

        # Пагинатор только у "Избранное". На первой странице должно быть на одно событие меньше из-за баннера
        first_page_count = None
        if int_or_none(self.prism) == 1:
            self.show_prism_paginator = True
            first_page_count = self.paginate_by - 1

        paginate = self.paginator_class(objects, self.paginate_by, first_page_count=first_page_count)

        try:
            objects = paginate.page(page)
        except (EmptyPage, InvalidPage):
            objects = paginate.page(1)

        return objects

    def get_events(self):
        """ Возвращает список событий """

        page = self.paginate(EventList(self, self.sessions))
        is_paginated = page.paginator.num_pages > 1
        return [page, page.object_list, is_paginated]

    def get_cinema_events(self):
        """ Возвращает список событий для кино
            полностью весь список + сортировка по количеству сеансов
            сеансы группируются по кинотеатрам
        """
        events = {}
        # Сворачиваем сеансы в dict вида
        # {
        #     event: {
        #         schedule: [{sessions: guide, sessions: [session...]}],
        #         cnt: <<sessions count>>
        #     }
        # }
        for session in self.prepopulate(self.sessions):
            guide = session.guide if session.guide else session.event_guide.guide_name

            if not session.event in events:
                events[session.event] = {
                    'schedule': [],
                    'cnt': 0
                }

            idx = 0
            for guide_sessions in events[session.event]['schedule']:
                if guide_sessions['guide'] == guide:
                    if session.time is not None:
                        events[session.event]['schedule'][idx]['sessions'].append(session)
                    break
                idx += 1
            else:
                events[session.event]['schedule'].append({
                    'guide': guide,
                    'date': session.date,
                    'is_3d': session.is_3d,
                    'sessions': [session] if session.time is not None else []
                })

            events[session.event]['cnt'] += 1
        events = sorted(events.items(), key=lambda i: i[1]['cnt'], reverse=True)
        for event, session_data in events:
            setattr(event, 'schedule', session_data['schedule'])
        return [None, [e[0] for e in events], False]

    def get_context_data(self, **kwargs):

        if self.event_type and hasattr(self, "get_%s_events" % self.event_type.alias):
            get_events = getattr(self, "get_%s_events" % self.event_type.alias)
        else:
            get_events = self.get_events

        filters = dict([(f.param, f) for f in self.filters])
        # Получаем список событий
        page, events, is_paginated = get_events()
        context = {
            'object_list': events,
            'page_obj': page,
            'is_paginated': is_paginated,
            'event_type': self.event_type,
            'current_date': self.current_date,
            'url_date': self.current_date or datetime.date.today(),
            'filters': filters,
            'view': self,
            'is_index_page': True,
            'prisms': Prism.objects.visible(),
            'prism': self.prism,
            'show_prism_paginator': self.show_prism_paginator,
        }
        return context


class AjaxEventsListView(EventsListView):
    """ Ajax endpoint
        фильтры передаются в качестве get параметров
    """

    def get_filter_data(self):
        return self.request.GET


class AjaxCalendarView(AjaxEventsListView):
    """ Ajax пагинатор по датам
        учитывает выбранные фильтры: тап события, заведение
        GET параметр month=201301
    """

    def get_context_data(self, **kwargs):
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


type_index = EventsListView.as_view(
    template_name=['afisha/%(event_type)s/index.html',
                   'afisha/event/index.html'],
    sessions_order='real_date')

events_list = AjaxEventsListView.as_view(
    template_name=['afisha/%(event_type)s/list.html',
                   'afisha/event/list.html'])

calendar_paginator = AjaxCalendarView.as_view(
    template_name=['afisha/tags/calendar-paginator.html'])


def calendar_carousel(request):
    event_id = int_or_none(request.GET.get('event_id'))

    try:
        date = request.GET.get('date')
        date = datetime.datetime.strptime(date, "%Y%m%d").date()
    except ValueError:
        date = datetime.date.today()

    event = get_object_or_404(Event, pk=event_id)

    calendar = CurrentSession.objects.filter(date__gte=date, event=event).values_list('date', flat=True).distinct() \
        .order_by('real_date')

    context = cinema_ajax_calendar_paginator(calendar, date, event)

    return render(request, 'afisha/tags/cinema-ajax-calendar-paginator.html', context)


@json_response
def extra_cinema(request):
    """
    Подгрузка дополнительных фильмов
    """

    start_index = int_or_none(request.GET.get('start')) or 0
    limit = int_or_none(request.GET.get('limit')) or DEFAULT_EXTRA_AJAX_COUNT

    controller = ExtraCinemaController()
    object_list, page_info = controller.get_events(start_index, limit)

    context = {
        'event_list': object_list,
        'request': request,
    }

    return dict(
        html=render_to_string('afisha/tags/afisha_extra_cinema_list.html', context, request=request),
        **page_info
    )


@json_response
def extra_culture(request):
    """
    Подгрузка дополнительных спектаклей
    """

    start_index = int_or_none(request.GET.get('start')) or 0
    limit = int_or_none(request.GET.get('limit')) or DEFAULT_EXTRA_AJAX_COUNT

    controller = ExtraCultureController()
    object_list, page_info = controller.get_events(start_index, limit)

    context = {
        'event_list': object_list,
        'request': request,
    }

    return dict(
        html=render_to_string('afisha/tags/afisha_extra_culture_list.html', context, request=request),
        **page_info
    )
