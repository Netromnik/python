# -*- coding: utf-8 -*-

from django import forms

from irk.profiles.forms.fields import UserAutocompleteField

from irk.push_notifications import models


class DeviceAdminForm(forms.ModelForm):
    user = UserAutocompleteField(label=u'Пользователь', required=False)

    class Meta:
        fields = '__all__'
        model = models.Device


class MessageAdminForm(forms.ModelForm):
    title = forms.CharField(
        label=u'Заголовок', max_length=26, help_text=u'Макс. 26 символов',
        widget=forms.TextInput(attrs={'class': 'vTextField'})
    )
    text = forms.CharField(
        label=u'Текст', max_length=80, widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}),
        help_text=u'Макс. 80 символов'
    )

    class Meta:
        fields = '__all__'
        model = models.Message
        help_texts = {
            'alias': u'Используется для специальных уведомлений'
        }
