# -*- coding: utf-8 -*-

import datetime

from django.contrib import admin

from irk.api.models import Application, _generate_key
from irk.api.forms import ApplicationAdminForm


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'access_token', 'created')
    readonly_fields = ('access_token', 'created')
    form = ApplicationAdminForm

    def save_model(self, request, obj, form, change):
        if not change:
            obj.access_token = _generate_key()
            obj.created = datetime.datetime.now()
        obj.save()

admin.site.register(Application, ApplicationAdmin)
