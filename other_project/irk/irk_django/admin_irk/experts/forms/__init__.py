# -*- coding: utf-8 -*-

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy

from irk.news.forms import BaseMaterialAdminForm
from irk.news.models import Category
from irk.phones.models import Firms
from irk.profiles.forms.fields import UserAutocompleteField
from irk.utils.fields.select import AjaxTextField

from irk.experts.models import Question


class ExpertAdminForm(BaseMaterialAdminForm):
    """Форма редактирования эксперта в админке"""

    firm = forms.ModelChoiceField(queryset=Firms.objects.all(), widget=forms.HiddenInput, required=False)
    user = UserAutocompleteField(label=u'Ведущий')
    category = forms.ModelChoiceField(label=u'Категория', queryset=Category.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(ExpertAdminForm, self).__init__(*args, **kwargs)
        self.fields['firm_name'] = AjaxTextField(
            url='/utils/objects/%d/?visible=True' % ContentType.objects.get_for_model(Firms).pk,
            callback='ObjectAutocompleteCallback', label=u'Фирма', required=False
        )
        instance = kwargs.get('instance')
        if instance and instance.firm:
            self.initial['firm_name'] = instance.firm.name


class QuestionInlineAdminForm(forms.ModelForm):
    """Форма инлайнового списка вопросов к пресс-конференции в админе"""

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and self.base_fields.get('same_as'):
            self.base_fields['same_as'].queryset = Question.objects.filter(expert=instance.expert,
                                                                           same_as__isnull=True).exclude(pk=instance.pk)
        super(QuestionInlineAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Question
        fields = ('same_as',)


class QuestionForm(forms.ModelForm):
    """Форма вопроса пользователя к пресс-конференции"""

    class Meta:
        model = Question
        fields = ('question',)


class ReplyForm(forms.Form):
    """Форма ответа на вопрос для ведущего конференции"""

    question = forms.ModelChoiceField(queryset=Question.objects.all(), widget=forms.HiddenInput())
    answer = forms.CharField(widget=forms.Textarea())
    action = forms.CharField(widget=forms.HiddenInput(), initial='reply')
