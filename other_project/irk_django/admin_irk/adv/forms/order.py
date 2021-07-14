# -*- coding: utf-8 -*-

from django import forms

from irk.adv.models import AdvOrder


class OrderForm(forms.ModelForm):

    class Meta:
        fields = ('service', 'client_name', 'client_email', 'client_contacts', 'description', 'link')
        model = AdvOrder
