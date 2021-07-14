# -*- coding: utf-8 -*-

import datetime

from django import forms
from django.contrib.auth.models import User

from irk.profiles.forms import NoneNamedSelectDateWidget
from irk.profiles.models import Profile

ONE_HUNDRED_YEARS = range(datetime.date.today().year - 100, datetime.date.today().year)


class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image',)


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(label=u'E-mail', required=False)
    birthday = forms.DateField(label=u'Дата рождения', widget=NoneNamedSelectDateWidget(years=ONE_HUNDRED_YEARS),
                               required=False)
    gender = forms.CharField(label=u'Пол', required=False, widget=forms.RadioSelect(choices=Profile.GENDER_CHOICES))

    class Meta:
        model = Profile
        fields = ('gender', 'birthday', 'image', 'subscribe', 'comments_notify')

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)

        self.initial['email'] = self.instance.user.email

    def save(self, commit=True):
        instance = super(ProfileUpdateForm, self).save(commit)

        user = User.objects.get(pk=instance.user_id)
        user.email = self.cleaned_data.get('email')
        user.save()

        return instance

    def clean_email(self):
        value = self.cleaned_data['email']

        if value and User.objects.filter(email=value).exclude(id=self.instance.user_id).exists():
            raise forms.ValidationError(u'Этот E-mail уже используется другим пользователем')

        return value

    def clean(self):
        email = self.cleaned_data.get('email')
        if not email:
            self.cleaned_data['comments_notify'] = False
            self.cleaned_data['subscribe'] = False
        return self.cleaned_data


class PasswordUpdateForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label=u'Новый пароль')
