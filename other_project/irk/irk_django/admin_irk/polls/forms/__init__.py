# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from irk.news.forms import BaseMaterialAdminForm
from irk.polls.forms.fields import TargetAutocompleteField
from irk.polls.models import PollChoice
from irk.polls.settings import POLL_OBJECTS


class PollAdminForm(BaseMaterialAdminForm):
    target_id = TargetAutocompleteField(label=u'Объект', required=False)

    def __init__(self, *args, **kwargs):
        super(PollAdminForm, self).__init__(*args, **kwargs)

        self.fields['start'].required = True
        self.fields['end'].required = True

        # Заполняем список возможных моделей
        # TODO: Можно не генерировать его каждый раз
        models = [('', u'-------'), ]
        for model_path in POLL_OBJECTS:
            app_label, model = model_path.split('.')
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                models.append((ct.pk, unicode(ct)))
            except ContentType.DoesNotExist:
                continue
        self.fields['target_ct'].choices = models

        # Если привязка к объекту уже есть, заполняем select с объектами
        if self.initial.get('target_ct'):
            try:
                content_type = ContentType.objects.get(pk=self.initial['target_ct'])
            except ContentType.DoesNotExist:
                return
            objects = content_type.model_class().objects.all().order_by('-pk')[:25]
            self.fields['target_id'].widget.choices = [(x.pk, unicode(x)) for x in objects]
            try:
                obj = content_type.get_object_for_this_type(pk=self.initial['target_id'])
            except ObjectDoesNotExist:
                return

            if obj not in self.fields['target_id'].widget.choices:
                self.fields['target_id'].widget.choices.append((obj.pk, unicode(obj)))

    def clean_target_id(self):
        target_id = self.cleaned_data.get('target_id')
        target_ct = self.cleaned_data.get('target_ct')
        if target_ct and target_id:
            try:
                target_ct.get_object_for_this_type(pk=target_id)
            except ObjectDoesNotExist:
                raise forms.ValidationError(u'Объекта этого типа не существует')
            else:
                return target_id

        return 0


class PollChoiceForm(forms.ModelForm):
    text = forms.CharField(widget=forms.TextInput(attrs={'size': 150}))

    class Meta:
        model = PollChoice
        exclude = ('votes_cnt',)
