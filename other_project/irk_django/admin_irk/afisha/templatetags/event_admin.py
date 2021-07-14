# -*- coding: UTF-8 -*-

import datetime
import operator

from django.db import connection
from django.template import Library, Node, Variable
from django.template.loader import render_to_string
from django.utils.http import urlencode

from irk.afisha import models
from irk.utils.user_options import City


class PeriodRender(Node):
    period = None
    def __init__(self,eg):
        self.eg = Variable(eg)

    def render(self,context):
        try:
            eg = self.eg.resolve(context)
            form = context['inline_admin_formset'].formset.eg_forms[eg.pk]
            context = {
                'eg': eg,
                'form': form,
                }
            return render_to_string('afisha/admin/periods.html', context)
        except Exception,e:
            return ''


def do_period_form(parser, token):
        params = token.split_contents()
        return PeriodRender(params[1])



register = Library()
register.tag("period_form", do_period_form)

AFISHA_RENDER_QUERY = '''SELECT `afisha_event`.`id`, `afisha_event`.`title` as afisha_title, `afisha_genre`.`name`,
    `afisha_event`.`comments_cnt`, `afisha_eventguide`.`id`, `afisha_eventguide`.`guide_id`, `phones_firms`.`name` AS guide_title,
    `afisha_sessions`.`time`, `afisha_sessions`.`order_time`, `afisha_hall`.`id`, `afisha_hall`.`name`
    FROM `afisha_period`
    LEFT JOIN `afisha_eventguide` ON `afisha_eventguide`.`id` = `afisha_period`.`event_guide_id`
    LEFT JOIN `afisha_event` ON `afisha_eventguide`.`event_id` = `afisha_event`.`id`
    LEFT JOIN `afisha_sections` ON `afisha_event`.`type_id` = `afisha_sections`.`id`
    LEFT JOIN `afisha_guide` ON `afisha_eventguide`.`guide_id` = `afisha_guide`.`firms_ptr_id`
    LEFT JOIN `phones_address` ON `phones_address`.`firm_id` = `afisha_guide`.`firms_ptr_id`
    LEFT JOIN `phones_firms` ON `afisha_guide`.`firms_ptr_id` = `phones_firms`.`id`
    LEFT JOIN `afisha_genre` ON `afisha_event`.`genreID` = `afisha_genre`.`id`
    LEFT JOIN `afisha_sessions` ON `afisha_sessions`.`period_id` = `afisha_period`.`id`
    LEFT JOIN `afisha_hall` ON `afisha_hall`.`id` = `afisha_eventguide`.`hall_id`
    WHERE
        `afisha_period`.`start_date` <= '%s'
        AND `afisha_period`.`end_date` >= '%s'
        AND `afisha_sections`.`id` = %d
        AND `phones_address`.`city_id` = %d
'''

AFISHA_RENDER_EXTRA_QUERY = '''SELECT `afisha_event`.`id`, `afisha_event`.`title` as afisha_title, `afisha_genre`.`name`,
    `afisha_event`.`comments_cnt`, `afisha_eventguide`.`id`, 0, `afisha_eventguide`.`guide_name` AS guide_title,
    `afisha_sessions`.`time`, `afisha_sessions`.`order_time`, 0, NULL
    FROM `afisha_period`
    LEFT JOIN `afisha_eventguide` ON `afisha_eventguide`.`id` = `afisha_period`.`event_guide_id`
    LEFT JOIN `afisha_event` ON `afisha_eventguide`.`event_id` = `afisha_event`.`id`
    LEFT JOIN `afisha_sections` ON `afisha_event`.`type_id` = `afisha_sections`.`id`
    LEFT JOIN `afisha_genre` ON `afisha_event`.`genreID` = `afisha_genre`.`id`
    LEFT JOIN `afisha_sessions` ON `afisha_sessions`.`period_id` = `afisha_period`.`id`
    WHERE
        `afisha_period`.`start_date` <= '%s'
        AND `afisha_period`.`end_date` >= '%s'
        AND `afisha_sections`.`id` = %d
        AND `afisha_eventguide`.`guide_name` != ''
        AND `afisha_eventguide`.`guide_id` is NULL
'''

class AfishaRender(Node):
    period = None
    types  = None
    types_to_revers = []
    def __init__(self,types,period):
        self.types_to_revers = []
        try:
            ts = []
            for type in types:
                if type[0] in ["\"","\'"]: ts.append(type.strip("\"").strip("'"))
                else: self.types_to_revers.append(Variable(type))
            self.types = models.EventType.objects.filter(alias__in=ts)
        except models.EventType.DoesNotExist:
            pass

        self.period = Variable(period)

    def render(self, context):
        request = context['request']

        city_param =  City(request)
        current_datetime = context.get('date_on', datetime.datetime.now())

        period = self.period.resolve(context)
        if self.types_to_revers:
            for ev_type in self.types_to_revers:
                ev_type = ev_type.resolve(context)

        date = datetime.datetime.now()
        if isinstance(period, datetime.datetime):
            date = period
        elif 'date' in period:
            date = period['date']

        cursor = connection.cursor()
        cursor.execute(AFISHA_RENDER_QUERY % (date.date(), date.date(), ev_type[0].pk, city_param.value.pk))
        rows = cursor.fetchall()

        if city_param.value.pk == 1:
            cursor.execute(AFISHA_RENDER_EXTRA_QUERY % (date.date(), date.date(), ev_type[0].pk))
            rows += cursor.fetchall()

        set = {}
        for row in rows:
            set[row[0]] = []
        events = []

        for event_pk in set.keys():
            event_data = filter(lambda x: x[0]==event_pk, rows)

            eg_set = {}
            map(eg_set.__setitem__, [row[4] for row in event_data],[])
            eventguide_set = []

            for eg_pk in eg_set.keys():
                eg_data = filter(lambda x: x[4]==eg_pk, event_data)
                if eg_data[0][5]:
                    if eg_data[0][9]:
                        guide = models.Guide(pk=eg_data[0][5], name=eg_data[0][6])
                        event_guide = models.EventGuide(pk=eg_data[0][4], guide=guide, hall=models.Hall(id=eg_data[0][9], name=eg_data[0][10], guide=guide))
                    else:
                        event_guide = models.EventGuide(pk=eg_data[0][4], guide=models.Guide(pk=eg_data[0][5], name=eg_data[0][6]))
                else:
                    event_guide = models.EventGuide(pk=eg_data[0][4], guide_name=eg_data[0][6], guide=None)

                sessions =  filter(lambda x: x[0], sorted([(row[8], row[7]) for row in eg_data], key=operator.itemgetter(0)))
                if sessions:
                    start = sessions[0][0]
                    sessions = map(lambda x: models.Sessions(time=x[1]), sessions)
                    setattr(event_guide, 'sessions', sessions)
                else:
                    start = None

                eventguide_set.append((start, event_guide))

            eventguide_set = map(lambda x: x[1],sorted(eventguide_set, key=operator.itemgetter(0)))

            if event_data[0][2]:
                event = models.Event(pk=event_pk, title = event_data[0][1], genre=models.Genre(name=event_data[0][2]), comments_cnt=event_data[0][3])
            else:
                event = models.Event(pk=event_pk, title = event_data[0][1], comments_cnt=event_data[0][3] )

            setattr(event, 'eg_set', eventguide_set)
            setattr(event, 'current_date', current_datetime.date())
            events.append((len(eventguide_set),event))
        events = map(lambda x: x[1], sorted(events, key=operator.itemgetter(0), reverse=True))

        template_context = {
            'date': date,
            'events': events,
            'city_param': city_param,
        }

        return render_to_string('afisha/block.html', template_context, context)


def do_afisha(parser, token):
    params = token.split_contents()
    period = params.pop()
    del params[0]
    return AfishaRender(types = params,period = period)

register.tag("afisha", do_afisha)


class NavigationRenderNode(Node):
    """Навигация в гиде и афише"""
    
    def __init__(self, sessions, direction, slice):
        self.direction = direction
        self.slice  = slice
        self.sessions = Variable(sessions)

    def render(self, context):
        request = context['request']

        #Подготавливаем не наши GET параметры
        # TODO: собирать с помощью urllib2.urlencode
        get_params = request.GET.copy()
        if 'date' in get_params:
            del get_params['date']

        query = urlencode(get_params)

        sessions  = self.sessions.resolve(context)

        direction = self.direction
        date_to = date_from = date_range = None

        if self.direction in ["left", "<", "-"]:
            try:
                # Не показываем ссылки в прошлое
                if sessions.week()[0].date < datetime.date.today():
                    return ''
            except IndexError:
                pass

            try:
                date_to = sessions['prev']
                if date_to:
                    try:
                        date_from = sessions[-int(self.slice):].next()
                        if date_from.date > date_to.date:
                            date_from = date_to
                    except Exception,e:
                        date_from = date_to
            except:
                 pass
        else:
            try:
                date_from = sessions[int(self.slice)]
                if date_from:
                    date_range = sessions[int(self.slice):int(self.slice)*2 - 1]
                    while True:
                        try:
                            date_to = date_range.next()
                        except:
                            break
                    if not date_to:
                        date_to = date_from
            except:
                pass

        if date_from and date_to:
            return render_to_string('afisha/navigation.html', {'sessions':sessions, 'direction':direction,
                'request':request, 'date_from':date_from, 'date_to':date_to, 'date_range':date_range})
        else:
            return '' 
        
        
def do_navigation(parser, token):
    params = token.split_contents()

    return NavigationRenderNode(*params[1:])

register.tag("navigation", do_navigation)


@register.inclusion_tag('afisha/snippets/event_block.html', takes_context=True)
def event(context, event):
    context['event'] = event
    try:
        img = event.gallery.main_image()
        context['image'] = img.image
        context['alt'] = img.alt
    except:
        context['image'] = None

    context['is_today'] =  context['date'].date() == datetime.date.today()\

    return context

