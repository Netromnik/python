# -*- coding: utf-8 -*-

from django_select2.fields import AutoModelSelect2MultipleField

from irk.adv.models import Client


class ClientAutocompleteMultipleField(AutoModelSelect2MultipleField):
    queryset = Client.objects.filter(is_deleted=False, is_active=True)
    search_fields = ('name__icontains',)
