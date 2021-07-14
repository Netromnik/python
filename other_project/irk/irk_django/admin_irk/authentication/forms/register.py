# -*- coding: utf-8 -*-

import time

from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from irk.authentication import settings as app_settings
from irk.profiles.models import Profile


class RegisterFormMixin(forms.ModelForm):
    """Общие поля и правила валидации для форм ввода дополнительных данных"""

    email = forms.EmailField(label=u'E-mail', required=False)

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if not email:
            return email

        if not User.objects.filter(email=email).exists():
            return email

        raise forms.ValidationError(u'Пользователь с таким адресом электронной почты уже существует.')

    def save(self, commit=True):
        """Пользователь активен сразу после регистрации"""

        user = super(RegisterFormMixin, self).save(commit=False)

        while True:
            username = 'irk-{0}'.format(time.time())
            if not User.objects.filter(username=username).exists():
                user.username = username
                break

        password = self.cleaned_data.get('password')
        if password:
            user.password = make_password(self.cleaned_data['password'])
        else:
            user.set_unusable_password()

        if commit:
            user.save()

        return user


class RegisterForm(RegisterFormMixin):
    """Форма ввода дополнительных данных при регистрации с помощью email"""

    email = forms.EmailField(label=u'E-mail')
    name = forms.RegexField(label=u'Ваше будущее имя на сайте', max_length=30, min_length=3,
                            regex=app_settings.USERNAME_REGEXP,
                            help_text=u'В псевдониме можно использовать только буквы русского и латинского алфавита, '
                                      u'цифры, знаки дефиса, подчеркивания, точку и пробел.',
                            error_messages={
                                'invalid': u'Псевдоним может содержать только буквы русского и латинского алфавита, '
                                           u'цифры, знаки дефиса, подчеркивания, точку и пробел.'
                            })
    password = forms.CharField(label=u'Пароль', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label=u'Подтверждение пароля', widget=forms.PasswordInput)
    captcha = ReCaptchaField(label=u'Подтвердите, что вы не робот:', widget=ReCaptchaWidget())

    class Meta(RegisterFormMixin.Meta):
        fields = ('email', 'password', 'password_confirm', 'captcha')

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError(u'Введённые пароли не совпадают')

        return self.cleaned_data


class SocialRegisterForm(RegisterFormMixin):
    """Форма ввода дополнительных данных при регистрации с помощью социальной сети"""

    action = forms.CharField(initial='register', widget=forms.HiddenInput)
