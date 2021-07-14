# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime

from django.views.generic.base import TemplateView

from irk.afisha.views.events import EventList
from irk.afisha.views.base import AfishaMixin
from irk.options.models import Site

from irk.afisha.views.filters import week_filter, site_filter


class NewYearEventsListView(AfishaMixin, TemplateView):
    """ Список событий нового года"""

    sites = Site.objects.filter(slugs='newyear2014')
    filters = [week_filter, site_filter]
    sessions_order = 'fake_date'

    def get(self, request, *args, **kwargs):
        # date = datetime.date.today()
        self.event_type = self.get_event_type(request, *args, **kwargs)
        self.event_type_name = self.event_type.alias if self.event_type else ''

        self.current_date = self.get_date(request, *args, **kwargs)
        self.sessions = self.get_sessions(self.get_filters())

        return super(NewYearEventsListView, self).get(request, *args, **kwargs)

    def get_date(self, request, *args, **kwargs):
        """ Возвращает дату из запроса """
        week_date = request.GET.get('week', None)

        if week_date:
            return datetime.datetime.strptime(week_date, '%Y%m%d')
        else:
            return datetime.datetime.now()

    def get_data(self):
        return {
            'week': self.current_date,
        }

    def get_events(self):
        """ Возвращает список событий """

        return EventList(self, self.sessions)[:]

    def get_context_data(self, **kwargs):

        filters = dict([(f.param, f) for f in self.filters])
        # Получаем список событий
        events = self.get_events()

        dates = []
        object_list = []
        for event in events:
            event_date = event.schedule.first.date
            if event_date not in dates:
                dates.append(event_date)
                object_list.append({"date": event_date, "events": []})

            for obj in object_list:
                if obj["date"] == event_date:
                    obj["events"].append(event)

        context = {
            'object_list': object_list,
            'event_type': self.event_type,
            'end_date': datetime.datetime(2015, 1, 14),
            'current_date': self.current_date,
            'filters': filters,
            'view': self,
            'today': datetime.datetime.today()
        }

        return context


index = NewYearEventsListView.as_view(template_name=['newyear2014/afisha/index.html', ])