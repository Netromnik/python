# -*- coding: utf-8 -*-

import os.path

from django import forms
from django.contrib.contenttypes.models import ContentType

from irk.map.models import Country
from irk.map.fields import PointField, PointWidget
from irk.phones.models import Firms
from irk.phones.fields import FirmAutocompleteField
from irk.utils.fields.select import AjaxTextField
from irk.tourism.helpers import parse_date
from irk.tourism.models import Place, TourBase, Tour, Way, TourFirm

def get_place_ct():
    return ContentType.objects.get_for_model(Place)

def get_tourbase_ct():
    return ContentType.objects.get_for_model(TourBase)

def get_firms_ct():
    return ContentType.objects.get_for_model(Firms)


class PlaceForm(forms.ModelForm):

    country = forms.ModelChoiceField(queryset=Country.objects.all(), empty_label=None, initial=170)
    center = PointField(label=u'Центр', widget=PointWidget(field='center', type='sat', zoom=7), required=False)
    promo = forms.ModelChoiceField(queryset=Firms.objects.all(), widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['promo_name'] = AjaxTextField(
            url='/utils/objects/%s/' % get_firms_ct(), callback='ObjectAutocompleteCallback',
            label=u'Фирма спонсор', required=False
        )
        instance = kwargs.get('instance')
        if instance:
            if instance.promo:
                self.initial['promo_name'] = unicode(instance.promo)

    class Meta:
        fields = '__all__'
        model = Place


class TourForm(forms.ModelForm):

    dates = forms.CharField(label=u'Даты', required=True,
                            help_text=u'Например: 22.04.2019-05.05.2019, 24.04.2019-07.05.2019')

    class Meta:
        model = Tour
        exclude = ('hotels', 'firm', 'is_main', 'is_recommended', 'is_hot', 'is_hidden')

    def clean_file(self):
        file_ = self.cleaned_data.get('file')
        try:
            if file_ and hasattr(file_, 'name') and \
                    not os.path.splitext(file_.name)[1].lower() in ('.doc', '.rar', '.zip'):
                raise forms.ValidationError(u'Неправильный тип файла')
        except IndexError:
            raise forms.ValidationError(u'Неправильный тип файла')

        return file_

    def clean_dates(self):
        dates = self.cleaned_data.get('dates', '')

        dates = parse_date(dates)
        if not dates:
            raise forms.ValidationError(u'Неправильный формат даты')

        return dates


class TourAdminForm(forms.ModelForm):

    firm = FirmAutocompleteField(label=u'Фирма')

    class Meta:
        fields = '__all__'
        model = Tour


class WayForm(forms.ModelForm):
    trip = forms.CharField(label=u'Описание', widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))

    class Meta:
        model = Way
        fields = ('trip',)


class TourFirmAdminForm(forms.ModelForm):
    firm = forms.CharField(widget=forms.HiddenInput)
    place = forms.ModelChoiceField(queryset=Place.objects.all(), widget=forms.HiddenInput, required=False)
    base = forms.ModelChoiceField(queryset=TourBase.objects.all(), widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(TourFirmAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        self.fields['place_name'] = AjaxTextField(
            url='/utils/objects/%s/' % get_place_ct(), callback='ObjectAutocompleteCallback',
            label=u'Место отдыха', required=False
        )
        self.fields['base_name'] = AjaxTextField(
            url='/utils/objects/%s/' % get_tourbase_ct(), callback='ObjectAutocompleteCallback',
            label=u'Турбаза', required=False
        )
        if instance:
            if instance.place:
                self.initial['place_name'] = instance.place.title
            if instance.base and instance.base.firm:
                self.initial['base_name'] = instance.base.firm.name

    class Meta:
        model = TourFirm
        fields = ('firm', 'place', 'price', 'price_comment', 'base')
