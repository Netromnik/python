# -*- coding: utf-8 -*-

from django import forms

from irk.utils.fields.security import CaptchaField
from irk.profiles.forms.fields import UserAutocompleteField
from irk.newyear2014.models import TextContestParticipant, PhotoContestParticipant, Wish, Congratulation, GuruAnswer


class TextContestAuthenticatedParticipantForm(forms.ModelForm):
    class Meta:
        model = TextContestParticipant
        fields = ('name', 'title', 'content')


class TextContestAnonymousParticipantForm(forms.ModelForm):
    email = forms.EmailField(label=u'E-mail', required=True)

    class Meta:
        model = TextContestParticipant
        fields = ('name', 'email', 'title', 'content')


class PhotoContestAuthenticatedParticipantForm(forms.ModelForm):
    class Meta:
        model = PhotoContestParticipant
        fields = ('name', 'image', 'title', 'content')


class PhotoContestAnonymousParticipantForm(forms.ModelForm):
    email = forms.EmailField(label=u'E-mail', required=True)

    class Meta:
        model = PhotoContestParticipant
        fields = ('name', 'email', 'title', 'image', 'content')


class WishForm(forms.ModelForm):
    class Meta:
        model = Wish
        fields = ('content',)


class CongratulationForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': u'Текст поздравления'}), max_length=1000)
    sign = forms.CharField(widget=forms.TextInput(attrs={'placeholder': u'Ваше имя'}), max_length=255)

    class Meta:
        model = Congratulation
        fields = ('content', 'sign')


class CongratulationAdminForm(forms.ModelForm):
    user = UserAutocompleteField(label=u'Автор', required=False)

    class Meta:
        fields = '__all__'
        model = Congratulation


class AnonymousCongratulationForm(CongratulationForm):
    captcha = CaptchaField(label=u'Контрольные цифры:',
                           help_text=u'Введите сюда число, которое вы видите на картинке слева')


class GuruForm(forms.ModelForm):
    age = forms.CharField(widget=forms.TextInput(attrs={'placeholder': u'Ваш возраст'}))

    class Meta:
        model = GuruAnswer
        fields = ('gender', 'age')
