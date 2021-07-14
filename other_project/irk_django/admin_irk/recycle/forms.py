# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django import forms
from irk.recycle.models import Dot, Category


class DotForm(forms.ModelForm):
    class Meta:
        model = Dot
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название компании'}),
            'addres': forms.TextInput(attrs={'placeholder': 'Адрес'}),
        }


class CatForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
