# -*- coding: utf-8 -*-

from django_select2 import AutoModelSelect2MultipleField

from irk.phones.fields import FirmAutocompleteField
from irk.utils.fields.widgets.autocomplete import ClearableAutoHeavySelect2Widget

from irk.obed.models import Establishment


class EstablishmentAutocompleteMultipleField(AutoModelSelect2MultipleField):
    queryset = Establishment.objects.filter(visible=True).select_related('firms_ptr')
    search_fields = ('name__icontains',)


class EstablishmentAutocompleteField(FirmAutocompleteField):
    queryset = Establishment.objects.filter(visible=True).select_related('firms_ptr')
    widget = ClearableAutoHeavySelect2Widget
