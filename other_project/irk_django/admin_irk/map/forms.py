# -*- coding: utf-8 -*-

from django import forms

from irk.map.fields import PointField, PointWidget
from irk.map.models import Cooperative, Countryside


class CooperativeAdminForm(forms.ModelForm):
    point = PointField(label=u'Центр', widget=PointWidget(field='point', type='sat', zoom=13))

    class Meta:
        model = Cooperative
        fields = '__all__'


class CountrysideAdminForm(forms.ModelForm):
    point = PointField(label=u'Центр', widget=PointWidget(field='point', type='sat', zoom=13))

    class Meta:
        model = Countryside
        fields = '__all__'
