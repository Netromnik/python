# -*- coding: utf-8 -*-

from django_select2 import AutoModelSelect2Field
from irk.utils.fields.widgets.autocomplete import ClearableAutoHeavySelect2Widget

from irk.adv.models import Place


class PlaceAutocompleteField(AutoModelSelect2Field):
    queryset = Place.objects.filter(visible=True).order_by('name')
    search_fields = ('name__icontains',)
    widget = ClearableAutoHeavySelect2Widget
