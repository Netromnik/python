# -*- coding: utf-8 -*-

import datetime

from irk.utils.search import ModelSearch

from irk.phones.search import FirmSearch


class GuideSearch(FirmSearch):
    fields = FirmSearch.fields + ('title_short', 'article', 'menu')
    boost = {
        'name': 1.0,
        'alternative_name': 0.75,
        'description': 0.5,
        'title_short': 0.8,
        'article': 0.2,
        'menu': 0.2,
    }


class EventSearch(ModelSearch):
    fields = ('title', 'caption', 'original_title', 'production', 'info', 'content', 'type_id', 'is_hidden')
    boost = {
        'title': 1.0,
        'original_title': 1.0,
        'content': 0.8,
        'caption': 0.5,
        'production': 0.3,
        'info': 0.3,
    }

    def get_queryset(self):
        from irk.afisha.models import CurrentSession

        now = datetime.datetime.now()
        events_ids = CurrentSession.objects.filter(end_date__gte=now, is_hidden=False).distinct().values_list('event_id', flat=True)

        return self.model.objects.filter(id__in=events_ids)
