# -*- coding: utf-8 -*-

import datetime

from django import forms
from django.contrib.contenttypes.models import ContentType

from irk.polls.models import Poll, PollChoice


class PollInlineFormset(forms.models.BaseInlineFormSet):
    parent_instance = None

    def __init__(self, *args, **kwargs):

        try:
            self.parent_instance = kwargs['instance']
            kwargs['instance'] = kwargs['instance'].poll.all()[0]
        except(KeyError, AttributeError, IndexError):
            ct = ContentType.objects.get_for_model(kwargs['instance'])
            self.parent_instance = kwargs['instance']
            kwargs['instance'] = Poll(target_ct=ct, target_id=kwargs['instance'].pk)

        super(PollInlineFormset, self).__init__(*args, **kwargs)

    def get_instance_from_obj(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        if obj.pk:
            obj = Poll(target_ct=ct, target_id=obj.pk)
            obj.save()
        else:
            obj = Poll(target_ct=ct, target_id=obj.pk)

        return obj

    def save(self, *args, **kwargs):
        self.instance.title = self.parent_instance.title
        self.instance.start = datetime.datetime.today()

        if not self.instance.object_pk:
            self.instance.object_pk = self.original_instance.pk

        if not self.instance.pk:
            self.instance.save()

        super(PollInlineFormset, self).save(*args, **kwargs)


class PollForm(forms.ModelForm):
    class Meta:
        models = PollChoice
        fields = ('text',)


poll_formset = forms.models.inlineformset_factory(Poll, PollChoice, form=PollForm, formset=PollInlineFormset,
                                                  extra=2, max_num=10, can_delete=False, fields='__all__',)
