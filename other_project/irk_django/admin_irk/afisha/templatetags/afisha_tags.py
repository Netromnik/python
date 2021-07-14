# -*- coding: UTF-8 -*-

import datetime

from django import template
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Sum
from django.template.loader import render_to_string

from irk.afisha.controllers import (
    ExtraAnnouncementsController, ExtraCinemaController, ExtraMaterialController, ExtraCultureController,
    SliderAnnouncementsController,
)
from irk.afisha.models import CurrentSession, Event, EventType, Guide, Review
from irk.afisha.permissions import is_moderator
from irk.afisha.settings import DEFAULT_EXTRA_AJAX_COUNT, INDEX_EXTRA_MATERIAL
from irk.news.models import BaseMaterial, Block
from irk.options.models import Site
from irk.phones.models import Sections as Section
from irk.utils.helpers import get_object_or_none, get_week_range
from irk.utils.templatetags import parse_arguments

register = template.Library()


@register.inclusion_tag("afisha/tags/event-types.html", takes_context=True)
def afisha_main_menu(context):
    active_event_type = CurrentSession.objects.all().values_list('event_type_id', flat=True).distinct()
    event_type = context.get('event_type')
    section = context.get('section')
    is_index_page = context.get('is_index_page', False)
    sections = list(context.get('sections', Section.objects.filter(is_guide=True).order_by('position')))
    if section:
        select_more = sections.index(section) >= 3
    else:
        select_more = False

    # Находимся в гиде. (Выбрана ссылка "Места")
    guide_rubric = context.get('curr_rub')
    cinema_section = Section.objects.filter(slug='cinema').first()
    if cinema_section:
        # Находимся на главной странице гида (Кинотеатры)
        is_guide_index = guide_rubric == cinema_section.pk
    else:
        is_guide_index = False

    request = context.get('request', None)
    search_query = ''
    if request:
        is_event_create_form = reverse('afisha:event_create') == request.path
        search_query = request.GET.get('q')
    else:
        is_event_create_form = None

    return {
        'current_type': event_type,
        'event_types': EventType.objects.filter(is_visible=True).order_by("position"),
        'section': section,
        'active_event_type': active_event_type,
        'sections': sections,
        'is_index_page': is_index_page,
        'select_more': select_more,
        'is_guide_rubric': bool(guide_rubric),
        'is_guide_index': is_guide_index,
        'is_event_create_form': is_event_create_form,
        'q': search_query,
    }


@register.simple_tag
def afisha_paginator_url(view_name, view_kwargs, **kwargs):
    kwargs.update(view_kwargs)
    return reverse(view_name, kwargs=kwargs)


@register.inclusion_tag("afisha/tags/cinema-calendar-paginator.html")
def cinema_calendar_paginator(calendar, current_date, obj=None):

    if isinstance(obj, Guide):
        view_name = 'guide:read'
        sessions_view_name = 'guide:sessions'
        view_kwargs = {
            'firm_id': obj.id,
        }
    else:
        view_name = 'afisha:event_read' if obj else 'afisha:events_type_index'
        view_kwargs = {
            'event_type': 'cinema',
        }
        if obj:
            view_kwargs['event_id'] = obj.id
            sessions_view_name = 'afisha:event_sessions'
        else:
            sessions_view_name = 'afisha:events_list'

    calendar = list(calendar)
    today = datetime.date.today()
    if not current_date:
        current_date = today
    if type(current_date) is tuple:
        week_range = get_week_range(current_date[1])
    else:
        week_range = get_week_range(current_date)

    next_date = next((date for date in calendar if date > week_range[6]), None)
    prev_date = next((date for date in reversed(calendar) if date < week_range[0]), None)
    return {
        'is_current_week': today in week_range,
        'week_range': [(day, day in calendar) for day in week_range],
        'next': next_date,
        'prev': prev_date,
        'current_date': current_date,
        'today': today,
        'event_type_alias': 'cinema',
        'view_name': view_name,
        'sessions_view_name': sessions_view_name,
        'view_kwargs': view_kwargs,
    }


@register.inclusion_tag("afisha/tags/cinema-ajax-calendar-paginator.html")
def cinema_ajax_calendar_paginator(calendar, current_date, obj=None):
    """
    Блок календаря для расписания событий для объектов `obj'
    Подгрузка событий делается через AJAX

    Параметры::
        calendar : список объектов `datetime.date', которые отображаются в календаре
        current_date : дата, которая должна быть выделена в календаре
        obj : объект, для которого выводится расписание
    """

    calendar = sorted(list(calendar))
    today = datetime.date.today()
    if isinstance(obj, Guide):
        view_name = 'guide:read'
        sessions_view_name = 'guide:sessions'
        view_kwargs = {
            'firm_id': obj.id,
        }
    else:
        view_name = 'afisha:event_read' if obj else 'afisha:events_type_index'
        view_kwargs = {
            'event_type': 'cinema',
        }
        if obj:
            view_kwargs['event_id'] = obj.id
            sessions_view_name = 'afisha:event_session'
        else:
            sessions_view_name = 'afisha:events_list'

    def calendar_items():
        weeks = []
        week_index = 0
        if not calendar:
            return weeks, week_index
        start_date = min(calendar)
        week_range = get_week_range(start_date)
        date = week_range[0]
        while date <= max(calendar):
            next_week_date = date + datetime.timedelta(7)
            week = [date + datetime.timedelta(i) for i in range(7)]
            week = [(d, d in calendar) for d in week]
            if date <= current_date < next_week_date:
                week_index = len(weeks)
            weeks.append(week)
            date = next_week_date

        return weeks, week_index

    week_dates, current_week_index = calendar_items()

    return {
        'today': today,
        'calendar':  week_dates,
        'current_date': current_date,
        'event_type_alias': 'cinema',
        'view_name': view_name,
        'sessions_view_name': sessions_view_name,
        'view_kwargs': view_kwargs,
        'current_week_index': current_week_index,
        'obj': obj,
    }


@register.inclusion_tag("afisha/tags/week-paginator.html")
def week_paginator(date, end_date=None):
    today = datetime.datetime.today()

    current_monday = (datetime.datetime.strptime('%s %s 1' % (date.isocalendar()[0],
                                                              date.isocalendar()[1]-1), '%Y %W %w'))

    current_sunday = (datetime.datetime.strptime('%s %s 0' % ((date + datetime.timedelta(7)).isocalendar()[0],
                                                              date.isocalendar()[1]-1), '%Y %W %w'))

    prev_date = (date - datetime.timedelta(7))
    prev_monday = (datetime.datetime.strptime('%s %s 1' % (prev_date.isocalendar()[0],
                                                           prev_date.isocalendar()[1]-1), '%Y %W %w'))
    next_date = (date + datetime.timedelta(7))
    next_monday = (datetime.datetime.strptime('%s %s 1' % (next_date.isocalendar()[0],
                                                           next_date.isocalendar()[1]-1), '%Y %W %w'))
    if (prev_monday + datetime.timedelta(7)) <= today:
        prev_monday = None

    if next_monday > end_date:
        next_monday = None

    return {
        'next': next_monday,
        'prev': prev_monday,
        'current_monday': current_monday,
        'current_sunday': current_sunday
    }


@register.inclusion_tag("afisha/tags/guide-calendar-paginator.html")
def guide_calendar_paginator(calendar, selected_date, obj):
    if calendar:
        current_month_date = calendar[0]
        next_month_date = next((d for d in calendar if d.month != current_month_date.month), None)
    else:
        current_month_date = selected_date[1]
        next_month_date = None
    return {
        'current_month': current_month_date,
        'next_month': next_month_date,
        'selected_date': selected_date,
        'object': obj,
    }


@register.inclusion_tag("afisha/tags/announce_slider/layout.html", takes_context=True)
def announce_slider(context, event_type=None, header=None):
    """Блок анонсов в виде слайдера. Отображаются события и лонгриды афиши"""

    request = context['request']

    show_hidden = is_moderator(request.user)

    controller = SliderAnnouncementsController(event_type, show_hidden)
    announce_list = controller.get_announcements()

    return {
        'request': request,
        'announce_list': announce_list,
        'event_type': event_type,
        'header': header,
    }


@register.inclusion_tag("afisha/tags/cinema-afisha-block.html", takes_context=True)
def cinema_afisha(context, **kwargs):
    """Блок сегодня и скоро в кино"""

    now = datetime.datetime.now()

    def cinema_today():
        queryset = CurrentSession.objects \
            .filter(date=now.date(), real_date__gte=now, event_type__alias='cinema') \
            .values('event_id') \
            .annotate(sum=Sum('id'))

        events_ids = {session['event_id']: session['sum'] for session in queryset}
        events = Event.objects.filter(pk__in=events_ids.keys()).select_related('type', 'genre')

        events_info = sorted(
            [(event, events_ids[event.pk]) for event in events],
            key=lambda e: e[1],
            reverse=True,
        )

        return [event_info[0] for event_info in events_info]

    result = {
        'events_today': cinema_today(),
        'request': context.get('request'),
        'user': context.get('user'),
    }

    result.update(kwargs)

    return result


@register.simple_tag(takes_context=True)
def filter_choices(context, view, filter_object, variable=None, force_filter=None):
    context[variable] = filter_object.get_choices(view, force_filter)
    return ''


@register.filter
def cinemainfo(value):
    lists = []
    current_list = []
    current_head = None
    for line in value.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.endswith(":"):
            if current_head and current_list:
                list_str = "".join(["<dd>%s</dd>" % item for item in current_list])
                lists.append("<dt>%s</dt>%s" % (current_head, list_str))
            current_list = []
            current_head = line
        else:
            current_list.append(line)
    list_str = "".join(["<dd>%s</dd>" % item for item in current_list])
    lists.append("<dt>%s</dt>%s" % (current_head, list_str))
    return  "<dl>%s</dl>" % "".join(lists)


@register.inclusion_tag('afisha/tags/sidebar_materials.html', takes_context=True)
def afisha_sidebar_materials(context, review=None):
    """
    Блок с материалами, связанными с афишей. Выводится в сайдбаре. 
    
    review - сюда можно передать рецензию на материал, тогда она в списке
        выведется первой и не будет дублироваться среди остальных материалов.
        ex: review=event.review.last
    """

    afisha_site = Site.objects.get(slugs='afisha')
    query = BaseMaterial.longread_objects.filter(sites=afisha_site).exclude(is_advertising=True) \
        .filter(is_hidden=False).order_by('-stamp', '-pk')

    if review:
        # раз мы выведем рецензию первой, то она не должна дублироваться
        query = query.exclude(pk=review.pk)
    
    materials = query[:5]

    result = []
    if review:
        result = [review]
    
    return {
        'materials': result + [m.cast() for m in materials],
    }


@register.inclusion_tag('afisha/tags/afisha_extra_announcements.html', takes_context=True)
def afisha_extra_announcements(context, event_type=None, limit=8):
    """
    Блок дополнительных анонсов с ajax-подгрузкой

    Если указан event_type, выводятся соответствующие этому типу анонсы
    """

    # По умолчанию отображаются первые limit анонсов. Остальные подгружаются через ajax.
    start_index = 0
    controller = ExtraAnnouncementsController(event_type)
    object_list, page_info = controller.get_announce_events(start_index, limit)

    if event_type:
        url = reverse_lazy('afisha:announces:extra', kwargs={'event_type_alias': event_type.alias})
    else:
        url = reverse_lazy('afisha:announces:extra')

    return dict(
        announcement_list=object_list,
        url=url,
        event_type=event_type,
        request=context.get('request'),
        **page_info
    )


@register.inclusion_tag('afisha/tags/afisha_extra_cinema.html', takes_context=True)
def afisha_extra_cinema(context, event=None, limit=8):
    """
    Блок фильмов этой недели с ajax-подгрузкой
    """

    start_index = 0
    controller = ExtraCinemaController(event)
    object_list, page_info = controller.get_events(start_index, limit)

    url = reverse_lazy('afisha:events_extra_cinema')

    return dict(
        event_list=object_list,
        url=url,
        request=context.get('request'),
        **page_info
    )


@register.inclusion_tag('afisha/tags/afisha_extra_culture.html', takes_context=True)
def afisha_extra_culture(context, event=None, limit=8):
    """
    Блок спектаклей следующего месяца с ajax-подгрузкой
    """

    start_index = 0
    controller = ExtraCultureController(event)
    object_list, page_info = controller.get_events(start_index, limit)

    url = reverse_lazy('afisha:events_extra_culture')

    return dict(
        event_list=object_list,
        url=url,
        request=context.get('request'),
        **page_info
    )


@register.inclusion_tag('afisha/tags/afisha_extra_materials.html', takes_context=True)
def afisha_extra_materials(context, limit=6):
    """
    Блок дополнительных материалов с ajax-подгрузкой
    """

    limit = 9 if INDEX_EXTRA_MATERIAL else limit

    start_index = 0
    controller = ExtraMaterialController()
    object_list, page_info = controller.get_materials(start_index, limit)

    # 6 материалов должно быть только на первой странице
    page_info['next_limit'] = DEFAULT_EXTRA_AJAX_COUNT

    url = reverse_lazy('afisha:events_extra_materials')

    return dict(
        material_list=object_list,
        url=url,
        request=context.get('request'),
        **page_info
    )


@register.inclusion_tag('afisha/tags/sidebar_materials.html', takes_context=True)
def afisha_materials_read_sidebar_block(context):
    """
    Блок материалов в правой колонке на страницах событий.

    Материалы для блока устанавливаются в админке новостей.
    """

    block = get_object_or_none(Block, slug='afisha_read_sidebar')
    if not block:
        return {}

    materials = []
    for position in block.positions.all():
        if not position.material:
            continue
        if position.material.is_hidden:
            continue
        materials.append(position.material)

    return {
        'materials': materials,
        'request': context.get('request'),
    }


@register.tag
def event_card(parser, token):
    """
    Карточка события

    Параметры:

    """

    bits = token.split_contents()
    args, kwargs = parse_arguments(parser, bits[1:])

    return EventCardNode(*args, **kwargs)


class EventCardNode(template.Node):
    """Нода для карточки события"""

    def __init__(self, event, **kwargs):
        self._event = event
        self._kwargs = kwargs

    def render(self, context):
        event = self._event.resolve(context)
        kwargs = {key: value.resolve(context) for key, value in self._kwargs.items()}

        review_url = None
        review = Review.material_objects.filter(event=event).only('stamp', 'slug', 'content_type', 'project').last()
        if review:
            review_url = review.get_absolute_url()

        try:
            event_image = event.gallery.main_image().image
        except AttributeError:
            event_image = None

        template_context = {
            'event': event,
            'event_image': event_image,
            'review_url': review_url,
        }
        template_context.update(kwargs)

        return render_to_string('afisha/tags/event_card.html', template_context, request=context.get('request'))


@register.simple_tag
def afisha_min_price(sessions):
    """Получить минимальную цену билета среди сеансов"""

    prices = []
    for s in sessions:
        if s.min_price:
            prices.append(s.min_price)

    if prices:
        return u'от {} руб.'.format(min(prices))
    else:
        return u''
