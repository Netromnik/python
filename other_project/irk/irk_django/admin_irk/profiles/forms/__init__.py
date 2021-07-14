# -*- coding: utf-8 -*-

import types
import datetime

from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import Select
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from irk.utils.fields.select import AjaxTextField
from irk.profiles.models import Profile, UserBanHistory, ProfileBannedUser
from irk.profiles.helpers import check_password
from irk.authentication.settings import USERNAME_REGEXP


# TODO: перенести в `utils.fields.widgets`
class NoneNamedSelectDateWidget(SelectDateWidget):
    day_none_value = (0, u'День')
    month_none_value = (0, u'Месяц')
    year_none_value = (0, u'Год')

    def create_select(self, name, field, value, val, choices, none_value):
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        if not (self.is_required and val):
            if field == self.day_field:
                choices.insert(0, self.day_none_value)
            elif field == self.month_field:
                choices.insert(0, self.month_none_value)
            elif field == self.year_field:
                choices.insert(0, self.year_none_value)
            else:
                choices.insert(0, self.none_value)
        local_attrs = self.build_attrs(id=field % id_)
        s = Select(choices=choices)
        select_html = s.render(field % name, val, local_attrs)
        return select_html


# TODO: docstring
# TODO: перенести в `profiles.forms.admin`
class UserAdminForm(forms.ModelForm):
    username = forms.RegexField(label=u'Логин', max_length=30, regex=USERNAME_REGEXP,
                                help_text=u'В логине можно использовать только буквы латинского алфавита, цифры, знаки дефиса и подчеркивания.')

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'user_permissions',
            'last_login', 'date_joined', 'groups')


# TODO: docstring
# TODO: перенести в `profiles.forms.admin`
class UserAddAdminForm(UserAdminForm):
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label=u'Подтвердите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username',)


# TODO: docstring
class ProfileBanForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False, label=u'Пользователь',
                                  widget=forms.HiddenInput())
    user_name = AjaxTextField(url='', callback='ObjectAutocompleteCallback', label=u'Пользователь', required=False)
    period = forms.IntegerField(label=u'Период',
                                widget=forms.Select(choices=zip(settings.BAN_PERIODS, settings.BAN_PERIODS)))
    reason = forms.CharField(label=u'Причина', widget=forms.Textarea, required=False)

    class Meta:
        model = ProfileBannedUser
        fields = ('is_banned', 'user')

    def __init__(self, *args, **kwargs):
        super(ProfileBanForm, self).__init__(*args, **kwargs)
        self.fields['user_name'].url = reverse('utils.views.get_objects',
                                               kwargs={'id': ContentType.objects.get_for_model(User).pk})
        self.fields['user_name'].widget.url = reverse('utils.views.get_objects',
                                                      kwargs={'id': ContentType.objects.get_for_model(User).pk})
        if self.initial.get('user'):
            if isinstance(self.initial.get('user'), (types.IntType, types.LongType)):
                user = User.objects.get(pk=self.initial['user'])
            else:
                user = self.initial['user']
            self.instance = user.profile
            self.initial['user_name'] = user.username
            try:
                history = UserBanHistory.objects.filter(user=user).order_by('-created')[0]
                self.initial['reason'] = history.reason
            except IndexError:
                pass

    def clean_user(self):
        if self.cleaned_data.get('user'):
            self.instance = self.cleaned_data['user'].profile
        else:
            raise forms.ValidationError(u'Неправильный ник пользователя')

        return self.cleaned_data['user']

    def save_m2m(self):
        pass


# TODO: docstring
class ProfileAdminInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileAdminInlineForm, self).__init__(*args, **kwargs)
        ban_text = ''
        try:
            if self.instance and hasattr(self.instance, 'user'):
                ban = UserBanHistory.objects.filter(user=self.instance.user).order_by('-created')[0]
                ban_text = u'Забанен до {}'.format(ban.ended) if ban.ended else u'Забанен навсегда.'
                ban_text += u' {}: {}'.format(ban.moderator, ban.reason)
        except IndexError:
            pass
        self.fields['is_banned'].help_text = ban_text

    signature = forms.CharField(label=u'Подпись', widget=forms.Textarea, required=False,
                                help_text=u'Используется в ответных письмах пользователям, можно использовать BB коды')

    description = forms.CharField(label=u'Подпись для блога', required=False, max_length=115,
                                  widget=forms.Textarea(attrs={'rows': 3}),
                                  help_text=u'Максимальное количество символов не более 115')

    class Meta:
        model = Profile
        fields = '__all__'
