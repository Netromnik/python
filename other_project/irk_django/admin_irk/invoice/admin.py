# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from utils.admin import ReadOnlyAdmin
from invoice.models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(ReadOnlyAdmin):
    list_display = ('number', 'status', 'invoice', 'amount', 'currency', 'created', 'performed_datetime')
    fields = ('number', 'status', 'invoice', 'amount', 'currency', 'created', 'performed_datetime')
