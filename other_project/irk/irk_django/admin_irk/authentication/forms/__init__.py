# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _
from social_django.models import UserSocialAuth

from irk.profiles.models import Profile
from irk.utils.helpers import normalize_number

AUTHENTICATION_FORM_FIELD_ERROR_MESSAGES = {
    'required': u'Незаполнен телефон, E-mail или пароль',
    'invalid': u'Неправильный телефон, E-mail или пароль',
}


class AuthenticationForm(BaseAuthenticationForm):
    """Форма аутентификации на сайте"""

    username = forms.CharField(label=u'Логин или E-mail', max_length=50, required=False,
                               error_messages=AUTHENTICATION_FORM_FIELD_ERROR_MESSAGES)
    password = forms.CharField(label=u'Пароль', widget=forms.PasswordInput, required=True,
                               error_messages=AUTHENTICATION_FORM_FIELD_ERROR_MESSAGES)
    remember = forms.BooleanField(label=u'запомнить меня', required=False,
                                  help_text=u'Не нужно будет вводить логин и пароль повторно. '
                                            u'В вашем браузере должны быть включены cookies.')

    phone_email = forms.CharField(label=u'Введите номер телефона или адрес электронной почты', max_length=100,
                                  required=True)

    def clean(self):
        phone_email = self.cleaned_data.get('phone_email')
        if phone_email:
            if '@' in phone_email:
                try:
                    user = User.objects.get(email=phone_email)
                except User.DoesNotExist:
                    raise forms.ValidationError(u'Неправильный телефон, E-mail или пароль')
            else:
                try:
                    user = User.objects.get(profile__phone=phone_email)
                except User.DoesNotExist:
                    raise forms.ValidationError(u'Неправильный телефон, E-mail или пароль')
            self.cleaned_data['username'] = user.username
        else:
            raise forms.ValidationError(u'Неправильный телефон, E-mail или пароль')
        return super(AuthenticationForm, self).clean()

    def clean_phone_email(self):
        phone_email = self.cleaned_data['phone_email']
        if '@' in phone_email:
            validate_email(phone_email)

            if not User.objects.filter(email=phone_email).exists():
                raise forms.ValidationError(u'Пользователя с данной электронной почтой не существует')
        else:
            phone_email = str(normalize_number(phone_email))
            if not phone_email:
                raise forms.ValidationError(u'Введите номер телефона')

            if not Profile.objects.filter(phone=phone_email).exists():
                raise forms.ValidationError(u'Пользователя с данным номером телефона не существует')

        return phone_email


AuthenticationForm.error_messages.update({
    'invalid_login': u'Неправильный телефон, E-mail или пароль',
})


class SocialAuthenticationForm(BaseAuthenticationForm):
    """Форма аутентификации при заходе на сайт через социальную сеть и выбора ссылки «у меня уже есть аккаунт»"""

    username = forms.CharField(label=_("Username"), max_length=30, required=False)
    email = forms.EmailField(label=u'E-mail', required=True)
    action = forms.CharField(initial='auth', widget=forms.HiddenInput)

    def __init__(self, backend_name=None, *args, **kwargs):
        self.backend_name = backend_name
        super(SocialAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
            self.cleaned_data['username'] = user.username
        except User.DoesNotExist:
            raise forms.ValidationError(self.error_messages['invalid_login'])
        if UserSocialAuth.get_social_auth_for_user(user).filter(provider=self.backend_name).exists():
            raise forms.ValidationError(u'Аккаунт уже имеет привязку к выбранной соц. сети')

        return super(SocialAuthenticationForm, self).clean()


SocialAuthenticationForm.error_messages.update({
    'invalid_login': u'Неправильный E-mail или пароль',
})


class RemindForm(forms.Form):
    """ Форма восстановления пароля """

    email = forms.CharField(label=u'Введите адрес электронной почты', max_length=100,
                                  required=True)

    def clean_email(self):
        email = self.cleaned_data['email']

        validate_email(email)

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(u'Пользователя с данной электронной почтой не существует')

        return email
