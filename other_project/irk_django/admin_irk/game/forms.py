# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django import forms

from irk.game.models import Treasure


class TreasureAdminForm(forms.ModelForm):
    hint = forms.CharField(label=u'Подсказка', widget=forms.Textarea)

    class Meta:
        model = Treasure
        fields = '__all__'
