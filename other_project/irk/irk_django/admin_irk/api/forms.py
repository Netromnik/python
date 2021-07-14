# -*- coding: utf-8 -*-

from django import forms

from irk.api.models import Application


class ApplicationAdminForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ('title',)
