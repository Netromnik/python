# # -*- coding: utf-8 -*-
#
# from django_select2 import AutoModelSelect2Field, AutoHeavySelect2Widget
# from django_select2.forms import HeavySelect2Mixin, HeavySelect2Widget
# from irk.adv.models import Client
#
#
# class ClientAutocompleteField(AutoModelSelect2Field):
#     queryset = Client.objects.filter(is_active=True, is_deleted=False).order_by('name')
#     search_fields = ('name__icontains',)
#     widget = AutoHeavySelect2Widget
