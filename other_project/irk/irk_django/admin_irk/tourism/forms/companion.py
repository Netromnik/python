# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse_lazy
from django.contrib.contenttypes.models import ContentType
from irk.tourism.models import Companion, Place

from irk.utils.decorators import strip_fields
from irk.utils.fields.select import AjaxTextField


@strip_fields
class CompanionForm(forms.ModelForm):
    """Форма добавления объявления компаньона"""

    class Meta:
        fields = '__all__'
        model = Companion

    def __init__(self, *args, **kwargs):
        super(CompanionForm, self).__init__(*args, **kwargs)

        self.fields['place'] = AjaxTextField(
            url=reverse_lazy('utils.views.get_objects', args=[ContentType.objects.get_for_model(Place).pk, ]),
            callback='PlaceAutocompleteCallback',
            label=u'Место отдыха', required=True
        )


@strip_fields
class CompanionSearchForm(CompanionForm):
    """Форма поиска компаньона"""

    class Meta:
        fields = ('place', 'my_composition', 'find_composition')
        model = Companion

    def __init__(self, *args, **kwargs):
        super(CompanionSearchForm, self).__init__(*args, **kwargs)

        self.fields['place'] = AjaxTextField(
            url=reverse_lazy('utils.views.get_objects', args=[ContentType.objects.get_for_model(Place).pk, ]),
            callback='PlaceAutocompleteCallback',
            label=u'Место отдыха', required=True
        )
