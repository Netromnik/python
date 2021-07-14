# -*- coding: utf-8 -*-

from django import forms
from django.contrib.contenttypes.models import ContentType

from irk.phones.models import Sections
from irk.tourism.models import Hotel, TourBase, TourFirm
from irk.phones.forms import FirmForm as BaseFirmForm, SectionFirmAdminForm as BaseFirmAdminForm


CHOICES = (
    ('hotel', u'Гостиницы'),
    ('tourbase', u'Турбазы'),
    ('tourfirm', u'Турфирмы'),
)


class TourismFirmMixin(object):

    CHOICES_MODELS = {
        'hotel': Hotel,
        'tourbase': TourBase,
        'tourfirm': TourFirm,
    }

    def __init__(self, *args, **kwargs):
        super(TourismFirmMixin, self).__init__(*args, **kwargs)
        self.initial['models'] = filter(lambda m: m[1].objects.filter(pk=self.instance.pk).exists(),
                                        self.CHOICES_MODELS.items())
        self.initial['models'] = [x[0] for x in self.initial['models']]


class HotelForm(TourismFirmMixin, BaseFirmForm):
    """Форма создания/редактирования отеля на клиенте"""

    models = forms.MultipleChoiceField(choices=CHOICES, label=u'Рубрики', widget=forms.CheckboxSelectMultiple)
    section = forms.ModelMultipleChoiceField(queryset=Sections.objects.all(),
                                             widget=forms.MultipleHiddenInput, required=False)

    class Meta:
        model = Hotel
        fields = BaseFirmForm.Meta.fields + ('place', 'price', 'price_comment', 'logo', 'level', 'category', 'season')


class HotelAdminForm(BaseFirmAdminForm):

    class Meta:
        model = Hotel
        fields = BaseFirmAdminForm.Meta.fields + ('place', 'price', 'price_comment', 'logo', 'level', 'category',
                                                  'promo', 'season')


class TourBaseForm(TourismFirmMixin, BaseFirmForm):
    """Форма создания/редактирования турбазы на клиенте"""

    models = forms.MultipleChoiceField(choices=CHOICES, label=u'Рубрики', widget=forms.CheckboxSelectMultiple)
    section = forms.ModelMultipleChoiceField(queryset=Sections.objects.all(),
                                             widget=forms.MultipleHiddenInput, required=False)

    class Meta:
        model = TourBase
        fields = BaseFirmForm.Meta.fields + ('place', 'price', 'price_comment', 'logo', 'promo', 'season')


class TourBaseAdminForm(BaseFirmAdminForm):
    # center = PointField(label=u'Центр', widget=PointWidget(type='sat', zoom=8), required=False)

    class Meta:
        model = TourBase
        fields = BaseFirmAdminForm.Meta.fields + ('place', 'price', 'price_comment', 'logo', 'promo', 'season')


class TourFirmForm(TourismFirmMixin, BaseFirmForm, ):
    """Форма создания/редактирования турфирмы на клиенте"""

    models = forms.MultipleChoiceField(choices=CHOICES, label=u'Рубрики', widget=forms.CheckboxSelectMultiple)
    section = forms.ModelMultipleChoiceField(queryset=Sections.objects.all(),
                                             widget=forms.MultipleHiddenInput, required=False)

    class Meta:
        model = TourFirm
        fields = BaseFirmForm.Meta.fields + ('skype', 'place', 'price', 'price_comment', 'logo', 'promo', 'base')


class TourFirmAdminForm(BaseFirmAdminForm):
    class Meta:
        model = TourFirm
        fields = BaseFirmAdminForm.Meta.fields + ('skype', 'place', 'price', 'price_comment', 'logo', 'promo', 'base')
