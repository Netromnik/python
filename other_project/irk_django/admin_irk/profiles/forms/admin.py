# -*- coding: utf-8 -*-

from django import forms

from irk.profiles.models import Profile
from irk.utils.helpers import normalize_number


class CorporativeProfileAdminForm(forms.ModelForm):
    email = forms.EmailField(label=u'E-mail', required=False)
    phone = forms.CharField(label=u'Телефон', max_length=20, required=True)

    class Meta:
        model = Profile
        fields = ('full_name', 'company_name', 'type', 'image', 'phone')

    def __init__(self, *args, **kwargs):
        super(CorporativeProfileAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.user_id:
            self.initial['email'] = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data['email']

        if email and self.instance:
            if Profile.objects.filter(user__email=email).exists():
                raise forms.ValidationError(u'Уже есть пользователь с таким email: {}'.format(email))

        return email

    def clean_phone(self):
        value = normalize_number(self.cleaned_data['phone'])
        if value and self.instance:
            qs = Profile.objects.filter(phone=value)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            try:
                profile = qs.get()
            except Profile.DoesNotExist:
                pass
            else:
                raise forms.ValidationError(u'Уже есть пользователь {} с таким номером телефона'.format(profile))

        return value


class ChangePasswordProfileAdminForm(forms.Form):
    """Форма изменения пароля в админе пользователей"""

    password = forms.CharField(label=u'Пароль')
