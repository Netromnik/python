# -*- coding: utf-8 -*-

from django import forms

from irk.adwords.models import AdWord, AdWordPeriod


class AdWordForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'size': 165}), label=u'Заголовок')
    caption = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': '100'}),
                              label=u'Подводка', required=False)
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 20, 'cols': '100'}),
                              label=u'Содержание', required=False)

    class Meta:
        model = AdWord
        fields = '__all__'


class AdWordPeriodForm(forms.ModelForm):
    class Meta:
        model = AdWordPeriod
        fields = '__all__'
