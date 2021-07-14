# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django_filters import DateFromToRangeFilter, DateFilter, CharFilter, NumberFilter
from django_filters import FilterSet

from irk.adv.models import Log, Banner
from django_filters import Filter
from django import forms


class IntegerFilter(Filter):
    field_class = forms.IntegerField


# class LogFilterSet(FilterSet):
#     # date = DateFromToRangeFilter(name='date')
#     date_start = DateFilter(name='date', lookup_expr='gte')
#     date_end = DateFilter(name='date', lookup_expr='lte')
#     # action = NumberFilter(name='action', lookup_expr='exact')
#
#     class Meta:
#         model = Log
#         # fields = ['date_start', 'date_end', 'action']
#         fields = ['date', 'action']


class BannerFilterSet(FilterSet):
    # width = IntegerFilter(name='width')

    class Meta:
        model = Banner
        fields = ['width', ]
