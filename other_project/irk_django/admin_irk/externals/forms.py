# -*- coding: utf-8 -*-

from django import forms

from irk.externals.models import InstagramMedia


class InstagramMediaAdminForm(forms.ModelForm):

    class Meta:
        model = InstagramMedia
        fields = ('is_visible', 'is_marked')
