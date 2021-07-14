# -*- coding: utf-8 -*-

import datetime
from collections import OrderedDict

from django.http import Http404
from django.shortcuts import get_object_or_404

from irk.afisha.models import EventType, CurrentSession, Event, Guide
from irk.utils.helpers import int_or_none


class AfishaMixin(object):
    """ Mixin-ы  для вьюх афиши
    """

    sessions_order = 'fake_date'

    def prepopulate(self, sessions):
        """ Для сеансов заполняет поля гида, события и т.д. """
        events = list(Event.objects.filter(id__in=[s.event_id for s in sessions]).prefetch_related('type', 'genre'))
        guides = list(Guide.objects.filter(id__in=[s.guide_id for s in sessions]))

        events = dict([(event.pk, event) for event in events])
        guides = dict([(guide.pk, guide) for guide in guides])

        for session in sessions:
            event = events.get(session.event_id)
            guide = guides.get(session.guide_id)
            if event:
                setattr(session, 'event', event)
            if guide:
                setattr(session, 'guide', guide)
        return sessions

    def get_event_type(self, request, *args, **kwargs):
        """ Возвращает текущий выбранный год """
        if 'event_type' in kwargs:
            return get_object_or_404(EventType, alias=kwargs.get('event_type'))
        elif 'type' in request.GET:
            pk = int_or_none(request.GET.get('type'))
            return get_object_or_404(EventType, pk=pk)

    def get_date(self, request, *args, **kwargs):
        """ Возвращает дату из запроса """
        if 'year' in kwargs:
            try:
                return datetime.date(int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
            except ValueError:
                raise Http404(u'Неверная дата')

    def get_template_names(self, event_type=None):
        if not event_type:
            event_type = self.event_type_name

        if type(self.template_name) in [list, tuple]:
            templates = self.template_name
        else:
            templates = super(AfishaMixin, self).get_template_names()

        context = {}
        if event_type:
            if type(event_type) in [str, unicode]:
                context['event_type'] = event_type
            else:
                context['event_type'] = event_type.alias

            return [tpl % context for tpl in templates]
        else:
            return templates

    def get_filters(self, data=None):
        """ Проходит по всем фильтрам, проверяя есть ли
            необходимые данные для формирования фильтра в исходных данных.

            return
                - filters - dict - обычные фильтры ORM
                - extra_filters - list
        """

        result = {
            'filters': {},
            'extra_filters': [],
        }

        filter_values = data or self.get_data()
        for param_filter in self.filters:
            if param_filter.param in filter_values or param_filter.required:
                value = filter_values.get(param_filter.param)
                filter_data = param_filter.get_filters(value, self)
                if type(filter_data) is dict:
                    result['filters'].update(filter_data)
                else:
                    result['extra_filters'].append(filter_data)
        return result

    def get_sessions(self, filters_data):
        """ Возвращает список сеансов для соответствующего типа
            или для главной страницы.

            filters - фильтры по дате/жанру/заведению/3d и т.д.
        """
        filters = filters_data.get('filters', {})
        filters.update({
            'end_date__gte': datetime.datetime.now(),
            'is_hidden': False,
        })
        current_sessions_qs = CurrentSession.objects.filter(**filters).order_by(self.sessions_order).with_tickets()\
            .prefetch_related('guide')
        for extra_filter in filters_data.get('extra_filters', []):
            current_sessions_qs = current_sessions_qs.filter(extra_filter)
        sessions = current_sessions_qs.select_related('period').order_by('real_date')

        # Для призмы выводим только уникальные события (первый сеанс)
        if getattr(self, 'prism', None):
            unique_sessions = OrderedDict()
            for session in sessions:
                if session.event not in unique_sessions:
                    unique_sessions[session.event] = session
            sessions = unique_sessions.values()

        return sessions

