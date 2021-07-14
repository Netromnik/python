# -*- coding: utf-8 -*-

from django_select2.fields import AutoHeavySelect2Widget, AutoModelSelect2Field

from irk.phones.models import Firms as Firm


class FirmAutocompleteField(AutoModelSelect2Field):
    """Автокомплит фирм"""

    queryset = Firm.objects.filter(visible=True)
    search_fields = ('name__icontains',)
    widget = AutoHeavySelect2Widget
