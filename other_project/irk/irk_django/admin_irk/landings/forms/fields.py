# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from irk.obed.models import Review

from django_select2 import AutoHeavySelect2Widget, AutoModelSelect2Field


class ReviewAutocompleteField(AutoModelSelect2Field):
    """Автокомплит обзоров"""

    queryset = Review.objects.filter(is_hidden=False)
    search_fields = ('title__icontains',)
    widget = AutoHeavySelect2Widget
