# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from irk.afisha.models import Event
from irk.utils.opensearch import BaseOpenSearchView


class EventsOpenSearch(BaseOpenSearchView):
    short_name = u'Афиша IRK.ru'
    description = u'Все самые интересные события Иркутска'
    use_suggestions = True

    def get_url(self):
        return '{}?q={{searchTerms}}'.format(reverse('afisha:search'))

    def get_suggestions(self, term):
        return [x[0][0] for x in Event.search.filter(_all=term).values_list('title')]
