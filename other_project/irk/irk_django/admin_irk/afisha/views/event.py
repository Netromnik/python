# -*- coding: utf-8 -*-

import httplib
import datetime
import logging
from collections import OrderedDict
from copy import deepcopy

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import F
from django.http import Http404, HttpResponseGone
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.encoding import force_unicode
from django.views.decorators.http import require_POST
from django.views.generic.detail import DetailView

from irk.afisha.models import Event, CurrentSession, Guide, EventType
from irk.afisha.search import EventSearch, GuideSearch
from irk.afisha.views.base import AfishaMixin
from irk.afisha.views.filters import (
    date_filter, event_filter, genre_filter, guide_filter, is_3d_filter, prism_filter, time_filter, type_filter
)
from irk.afisha.settings import PAST_EVENT_410_DAYS
from irk.utils.http import ajax_request
from irk.utils.search import ElasticSearchQuerySet

logger = logging.getLogger(__name__)


class EventReadView(AfishaMixin, DetailView):
    """ Страница просмотра события """

    model = Event
    pk_url_kwarg = 'event_id'
    filters = [date_filter, time_filter, type_filter, genre_filter, guide_filter,
               is_3d_filter, event_filter, prism_filter]

    def get_queryset(self):
        qs = super(EventReadView, self).get_queryset()
        qs = qs.filter(is_hidden=False)
        return qs

    def get(self, request, *args, **kwargs):
        self.event_type = self.get_event_type(request, *args, **kwargs)
        self.event_type_name = self.event_type.alias if self.event_type else ''
        self.date = self.get_date(request, *args, **kwargs)

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        # Редирект событий за прошедшие даты
        if self.date < datetime.date.today() and self.event_type.hide_past:
            return self.redirect_past_date(request, context)

        return self.render_to_response(context)

    def redirect_past_date(self, request, context):
        neareset_date = context['calendar'].first()
        if neareset_date:
            params = {
                'year': neareset_date.strftime('%Y'),
                'month': neareset_date.strftime('%m'),
                'day': neareset_date.strftime('%d'),
                'event_type': self.event_type_name,
                'event_id': self.object.pk,
            }
            return redirect(reverse('afisha:event_read', kwargs=params), permanent=True)

        # Показывать страницу с альтернативными событиями какое-то время после закрытия
        if self.date < datetime.date.today() + datetime.timedelta(PAST_EVENT_410_DAYS):
            events = Event.objects.filter(type=self.event_type, is_hidden=False).order_by('?')[:8]
            context = {
                'events': events,
            }
            response = render(request, 'afisha/event/past_event.html', context)
            response.status_code = httplib.GONE
            response.reason_phrase = httplib.responses[httplib.GONE]
            return response

        return redirect(reverse('afisha:events_type_index', kwargs={'event_type': self.event_type_name}),
                        permanent=True)

    def get_data(self):
        if self.object.type.alias == 'cinema':
            # Для кино фильтр только за конкретную дату
            return {
                'date': self.date,
            }
        elif self.object.type.alias in ['exhibitions', 'culture', 'sport']:
            # Для выставок расписание на 7 дней
            return {
                'date': ('seven', self.date),
            }
        else:
            return {}

    def get_context_data(self, **kwargs):
        today = datetime.date.today()

        # Только сеансы на которые можно купить билеты
        only_buy_tickets = self.request.GET.get('buy_tickets', None)

        # Расписание сеансов события
        schedule = OrderedDict()
        queryset = self.get_sessions(self.get_filters())

        # Kэш наличия билетов у заведений
        guide_has_tickets_cache = {}

        for session in queryset:
            guide = session.guide if session.guide else \
                Guide(name=session.event_guide.guide_name)

            if only_buy_tickets:
                if guide.pk not in guide_has_tickets_cache:
                    guide_has_tickets_cache[guide.pk] = guide.is_tickets_exist()
                if not guide_has_tickets_cache[guide.pk]:
                    continue
                elif not session.is_tickets_exist():
                    continue

            key = guide.schedule.get_key(session)
            if key not in schedule:
                schedule[key] = deepcopy(guide)
            schedule[key].schedule.append(session)

        calendar = CurrentSession.objects.filter(
            date__gte=today,
            event=self.object).values_list('date', flat=True).distinct().order_by('real_date')
        filters = dict([(f.param, f) for f in self.filters])
        context = {
            'event_type': self.event_type,
            'schedule': schedule.values(),
            'calendar': calendar,
            'current_date': self.date,
            'comments': self.request.GET.get('comments', None),
            'filters': filters,
            'view': self,
            'today': today,
            'any_2d': queryset.filter(is_3d=False, time__isnull=False).exists(),
            'any_3d': queryset.filter(is_3d=True).exists(),
            'can_buy_tickets': self._can_buy_tickets(queryset),
        }
        context_data = super(EventReadView, self).get_context_data(**context)

        for session in queryset:
            context_data['event'].schedule.append(session)

        return context_data

    def get_sessions(self, *args, **kwargs):
        qs = super(EventReadView, self).get_sessions(*args, **kwargs)
        qs = qs.filter(event=self.object)
        return qs

    def _can_buy_tickets(self, queryset):
        """Можно ли покупать билеты на это событие"""

        # Т.е. есть ли сеансы с привязкой к kassy.ru
        return queryset.filter(kassysession__isnull=False).exists()


read = EventReadView.as_view(
    template_name=['afisha/%(event_type)s/read.html',
                   'afisha/event/read.html'],
    sessions_order='real_date')

sessions = EventReadView.as_view(
    template_name=['afisha/%(event_type)s/sessions.html',
                   'afisha/event/sessions.html'])


def search(request):
    """Поиск по афише"""

    q = force_unicode(request.GET.get('q', '').strip())

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20

    try:
        event_type = EventType.objects.get(id=int(request.GET['type']))
    except (KeyError, EventType.DoesNotExist, ValueError, TypeError):
        event_type = None

    is_places = request.GET.get('is_places')

    base_query = {
        "size": 100,
        "min_score": 0.1,
        "query": {
            "filtered": {
                "query": {
                    "multi_match": {
                        "query": q,
                        "type": "best_fields",
                        "minimum_should_match": "70%",
                        "fuzziness": "1",
                        "fields": [],
                    }
                },
            }
        }
    }

    types = list(EventType.objects.all())

    # Поиск событий
    event_query = deepcopy(base_query)
    event_query['query']['filtered']['query']['multi_match']['fields'] = [
        '{}^{}'.format(k, v) for k, v in EventSearch.boost.items()
    ]
    event_query['query']['filtered']['filter'] = {"term": {"is_hidden": False}}
    # Доступные типы событий для поискового запроса
    available_types = {event.type_id for event in ElasticSearchQuerySet(Event).raw(event_query)}
    for type_ in types:
        setattr(type_, 'is_available', type_.id in available_types)

    if is_places:
        # Поиск заведений
        firm_query = deepcopy(base_query)
        firm_query['query']['filtered']['query']['multi_match']['fields'] = [
            '{}^{}'.format(k, v) for k, v in GuideSearch.boost.items()
        ]
        objects = ElasticSearchQuerySet(Guide).raw(firm_query)
    else:
        # Фильтруем события по типу
        if event_type:
            event_query['query']['filtered']['filter'] = {
                "bool": {
                    "must": [
                        {"term": {"is_hidden": False}},
                        {"term": {"type_id": event_type.id}}
                    ]
                }
            }
        objects = ElasticSearchQuerySet(Event).raw(event_query)

    paginate = Paginator(objects, limit)

    try:
        objects = paginate.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginate.page(paginate.num_pages)

    if not is_places:
        now = datetime.datetime.now()
        for obj in objects.object_list:
            try:
                obj_session = CurrentSession.objects.filter(event=obj, end_date__gte=now, is_hidden=False).select_related('event', 'period') \
                    .prefetch_related('event__type', 'event__genre').order_by('real_date')[0]
                obj.schedule.append(obj_session)
            except IndexError:
                continue

    context = {
        'q': q,
        'page': page,
        'limit': limit,
        'is_places': is_places,
        'objects': objects,
        'type': getattr(event_type, 'id', None),
        'types': types,
    }

    return render(request, 'afisha/search.html', context)


def event_redirect(self, *args, **kwargs):
    event_id = kwargs.get('event_id')
    event = get_object_or_404(Event, pk=event_id)
    kwargs.update({
        'event_type': event.type.alias
    })
    return redirect(reverse('afisha:event_read', kwargs=kwargs))


@require_POST
@ajax_request
def buy_button_click(request):
    """Пользователь нажал на кнопку «Купить билет»"""

    event_id = request.json.get('event_id')
    if not event_id:
        return {'ok': False, 'msg': u'Нет идентификатора события'}

    updates = Event.objects.filter(id=event_id).update(buy_btn_clicks=F('buy_btn_clicks') + 1)
    if updates:
        return {'ok': True, 'msg': u'Счетчик обновлен'}

    return {'ok': False, 'msg': u'Что-то пошло не так'}
