# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from irk.afisha.controllers import ExtraAnnouncementsController
from irk.afisha.models import CurrentSession, EventType, AnnouncementColor, Announcement
from irk.afisha.settings import DEFAULT_EXTRA_AJAX_COUNT
from irk.utils.helpers import int_or_none
from irk.utils.http import json_response


def colors_iterator():
    # TODO: `itertools.cycle`
    colors = list(AnnouncementColor.objects.all().order_by('position'))
    i = 0
    if colors:
        while True:
            yield colors[i].value
            i += 1
            if i >= len(colors):
                i = 0
    else:
        while True:
            yield 'ffffff'


def events_list(request, event_type=None):
    """ Анонсы событий """

    event_ids = list(Announcement.objects.active().values_list('event', flat=True))
    sessions_qs = CurrentSession.objects.filter(event_id__in=event_ids)
    # Получаем список всех уникальных типов событий
    # по которым есть анонсы
    current_event_types = list(sessions_qs.values_list('event_type_id', flat=True).distinct())
    if event_type:
        event_type = get_object_or_404(EventType, alias=event_type)
        sessions_qs = sessions_qs.filter(event_type_id=event_type.pk)

    sessions_qs = sessions_qs.order_by('real_date')
    events_data = {}
    for session in sessions_qs.select_related('event_guide', 'period', 'event__genre'):
        if session.event not in events_data:
            events_data[session.event] = session

    events = []
    for event, session in sorted(events_data.items(), key=lambda i: i[1].real_date):
        setattr(event, 'schedule', [{'date': session.date, 'price': session.period.price}])
        events.append(event)
    event_types = [(ev_type, ev_type.pk in current_event_types) for ev_type in EventType.objects.all().order_by("position")]
    context = {
        'events': events,
        'colors': colors_iterator(),
        'event_types_list': event_types,
        'event_type': event_type,
    }

    return render(request, 'afisha/event/announces.html', context)


@json_response
def extra_announcements(request, event_type_alias=None):
    """
    Подгрузка дополнительных событий с анонсами

    Если указан event_type_alias, то подгружаются события соответствующего типа
    """

    start_index = int_or_none(request.GET.get('start')) or 0
    limit = int_or_none(request.GET.get('limit')) or DEFAULT_EXTRA_AJAX_COUNT

    event_type = EventType.objects.filter(alias=event_type_alias).first()
    controller = ExtraAnnouncementsController(event_type)
    object_list, page_info = controller.get_announce_events(start_index, limit)

    context = {
        'announcement_list': object_list,
        'request': request,
    }

    return dict(
        html=render_to_string('afisha/tags/afisha_extra_announcements_list.html', context, request=request),
        **page_info
    )
