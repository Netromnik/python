# -*- coding: utf-8 -*-

import json
import urllib2

from django.db.models import Q
from django_select2.fields import AutoSelect2Field, AutoHeavySelect2Widget, AutoModelSelect2Field
from django_select2.views import NO_ERR_RESP

from irk.afisha.models import Guide, Event, Hall
from irk.utils.fields.widgets.autocomplete import ClearableAutoHeavySelect2Widget
from irk.utils.grabber import proxy_requests


class ImdbIdAutocompleteWidget(AutoHeavySelect2Widget):

    def render_texts(self, selected_choices, choices):
        return json.dumps(selected_choices)


class ImdbIdAutocompleteField(AutoSelect2Field):
    widget = ImdbIdAutocompleteWidget

    def get_results(self, request, term, page, context):
        choices = []
        response = proxy_requests.get('http://www.omdbapi.com/?i=&s={0}'.format(urllib2.unquote(term.encode("utf8")))).json()

        for item in response.get('Search', ()):
            choices.append([item['imdbID'], u'{0} ({1})'.format(item['Title'], item['Year'])])

        return 'nil', False, choices


class GuideAutocompleteWidget(AutoHeavySelect2Widget):
    def __init__(self, *args, **kwargs):
        super(GuideAutocompleteWidget, self).__init__(*args, **kwargs)

        # Позволяем вводить в поле автокомплита свои значения
        # https://groups.google.com/forum/#!searchin/select2/new$20value/select2/QoX0b9VH1l8/f8IXaA53kCQJ
        # https://gist.github.com/fmpwizard/4985356
        self.options['createSearchChoice'] = '*START*createSearchChoice*END*'

    def render_texts(self, selected_choices, choices):
        texts = []
        for choice in selected_choices:
            texts.append(unicode(choice))
        if texts:
            return json.dumps(texts)

    def render_inner_js_code(self, id_, *args):
        js = super(GuideAutocompleteWidget, self).render_inner_js_code(id_, *args)
        if args[1] and not isinstance(args[1], (str, unicode)):
            js += u"$('#{}').select2('val', '{}');".format(id_, args[1].pk)
        return js


class GuideAutocompleteField(AutoSelect2Field):
    queryset = Guide.objects
    search_fields = ('name__icontains', 'title_short__icontains')
    widget = GuideAutocompleteWidget

    def get_results(self, request, term, page, context):
        q_objects = Q()
        for field in self.search_fields:
            q_objects |= Q(**{field: term})

        queryset = self.queryset.filter(q_objects)

        queryset = queryset.values_list('id', 'name')
        res = [(obj[0], obj[1], {}) for obj in queryset]

        return (NO_ERR_RESP, False, res)

    def to_python(self, value):
        value = super(GuideAutocompleteField, self).to_python(value)
        if not value:
            return value

        if value.isdigit():
            try:
                return self.queryset.get(pk=value)
            except Guide.DoesNotExist:
                pass

        return value


class EventAutocompleteWidget(AutoHeavySelect2Widget):

    def render_texts_for_value(self, id_, value, choices):
        """Переопределяем метод, потому что в `django_select2.widgets.HeavySelect2Mixin.render_texts`
        делается выборка `self.queryset`, которая нигде не используется,
        но занимает много времени"""

        try:
            instance = Event.objects.get(id=value)
            return u"$('#{}').txt('{}');".format(id_, unicode(instance))
        except (ValueError, Event.DoesNotExist):
            return


class EventForGuideAutocompleteField(AutoModelSelect2Field):
    queryset = Event.objects.filter(is_hidden=False)
    search_fields = ('title__icontains', )
    widget = EventAutocompleteWidget


class EventClearableAutocompleteField(AutoModelSelect2Field):
    """Автодополнение для событий"""

    queryset = Event.objects.filter(is_hidden=False)
    search_fields = ('title__icontains', )
    widget = ClearableAutoHeavySelect2Widget


class GuideClearableAutocompleteField(AutoModelSelect2Field):
    """Автодополнение для заведений гида"""

    queryset = Guide.objects
    search_fields = ('name__icontains', 'title_short__icontains')
    widget = ClearableAutoHeavySelect2Widget


class HallClearableAutocompleteField(AutoModelSelect2Field):
    """Автодополнение для залов заведений гида"""

    queryset = Hall.objects
    search_fields = ('name__icontains', 'guide__name__icontains')
    widget = ClearableAutoHeavySelect2Widget

    def get_results(self, request, term, page, context):
        """Подготовка результатов автодополнения."""

        params = self.prepare_qs_params(request, term, self.search_fields)
        halls = self.queryset.filter(*params['or'], **params['and']).select_related('guide')
        choices = []
        for hall in halls:
            choices.append([
                hall.pk, u'{0.name} ({0.guide})'.format(hall), {}
            ])
        return 'nil', False, choices
