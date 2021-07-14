# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django import forms
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from irk.landings.forms.fields import ReviewAutocompleteField
from irk.utils.fields.geo import PointCharField
from irk.landings.models import Resume
from irk.landings.models import TreasureDish, Thank, QuestionsGovernor
from irk.obed.forms.fields import EstablishmentAutocompleteField
from irk.utils.files.admin import admin_media_static


class AnonymousResumeForm(forms.ModelForm):
    captcha = ReCaptchaField(label=u'Контрольные цифры:', widget=ReCaptchaWidget())

    class Meta:
        model = Resume
        fields = ('name', 'contact', 'attach', 'link', 'content', 'captcha')


class AuthResumeForm(forms.ModelForm):

    class Meta:
        model = Resume
        fields = ('name', 'contact', 'attach', 'link', 'content')


class TreasureDishAdminForm(forms.ModelForm):
    """Форма редактирования блюд в админе"""

    establishment = EstablishmentAutocompleteField(label=u'Заведение', required=True)
    review = ReviewAutocompleteField(label=u'Рецензия', required=False)

    class Meta:
        model = TreasureDish
        fields = '__all__'

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js',)


class Article9MayAdminForm(forms.ModelForm):
    """Форма для статьи 9 мая в админе"""

    point = PointCharField(label=u'Координата', help_text=u'Пример: 52.284398, 104.245209', required=False)


class ThankForm(forms.ModelForm):
    """Форма благодарности"""

    class Meta:
        model = Thank
        fields = ('name', 'text', 'contact')


class QuestionsGovernorForm(forms.ModelForm):
    """Форма вопроса губернатору"""

    class Meta:
        model = QuestionsGovernor
        fields = ('text', 'contact', 'locality')
