# -*- coding: utf-8 -*-

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.forms.utils import ErrorList

from irk.map.models import Cities, Streets
from irk.news.forms import ArticleAdminForm as ArticleBaseAdminForm
from irk.obed.forms.fields import EstablishmentAutocompleteMultipleField, EstablishmentAutocompleteField
from irk.obed.forms.widgets import BillCheckboxSelectMultiple, BillRadioSelect
from irk.obed.models import Establishment, GuruCause, Article, Type, Menu, Review
from irk.phones.forms import FirmForm, SectionFirmAdminForm
from irk.phones.models import Sections, Address
from irk.utils.fields.file import AdminImagePreviewWidget
from irk.utils.fields.select import AjaxTextField
from irk.utils.helpers import normalize_number


def get_establishment_ct():
    return ContentType.objects.get_for_model(Establishment)


def get_sections_for_establishment():
    return Sections.objects.filter(content_type=get_establishment_ct())


class GuruSearchForm(forms.Form):
    """Форма поиска Гуру"""

    cause = forms.ModelChoiceField(queryset=GuruCause.objects.all(), empty_label=None)


class EstablishmentForm(FirmForm):
    """Форма заведения"""

    section = forms.ModelMultipleChoiceField(label=u'Рубрики', queryset=None,
                                             widget=forms.CheckboxSelectMultiple())

    main_section = forms.ModelChoiceField(label=u'Рубрики', queryset=None,
                                          widget=forms.HiddenInput(), required=True)

    bill = forms.ChoiceField(label=u'Средний чек', choices=Establishment.BILL_CHOICES, widget=BillRadioSelect)
    business_lunch_price = forms.IntegerField(label=u'Минимальная стоимость бизнес-ланча', max_value=100000,
                                              min_value=0, widget=forms.TextInput, required=False)

    class Meta:
        model = Establishment
        fields = ('name', 'url', 'mail', 'contacts', 'description', 'section',
                  'main_section', 'types', 'bill', 'parking', 'facecontrol', 'card_image',
                  'wifi', 'dancing', 'karaoke', 'children_room', 'terrace', 'catering', 'business_lunch',
                  'cooking_class', 'breakfast', 'children_menu', 'cashless', 'live_music', 'entertainment',
                  'banquet_hall', 'business_lunch_price', 'business_lunch_time', )
        widgets = {
            'types': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(EstablishmentForm, self).__init__(*args, **kwargs)
        self.fields['section'].queryset = get_sections_for_establishment()
        self.fields['main_section'].queryset = get_sections_for_establishment()

    def clean(self):
        cleaned_data = super(EstablishmentForm, self).clean()

        # Если галочка бизнес-ланч установлена, то поля цены и времени бизнес-ланча обязательны
        business_lunch = cleaned_data.get('business_lunch')
        business_lunch_price = cleaned_data.get('business_lunch_price')
        business_lunch_time = cleaned_data.get('business_lunch_time')
        if business_lunch and not all([business_lunch_price, business_lunch_time]):
            msg = u'Не заполнено поле {}'
            if not business_lunch_price and 'business_lunch_price' not in self._errors:
                self._errors['business_lunch_price'] = self.error_class([msg.format(u'минимальная стоимость бизнес-ланча')])
                cleaned_data.pop('business_lunch_price', None)
            if not business_lunch_time and 'business_lunch_time' not in self._errors:
                self._errors['business_lunch_time'] = self.error_class([msg.format(u'время бизнес-ланча')])
                cleaned_data.pop('business_lunch_time', None)

        return cleaned_data


class EstablishmentAdminForm(SectionFirmAdminForm):
    """Форма заведения в админке"""

    guru_cause = forms.ModelMultipleChoiceField(queryset=GuruCause.objects.all(), label=u'Гуру (повод)', required=False)
    section = forms.ModelMultipleChoiceField(queryset=Sections.objects.none(), label=u'Рубрики', required=True)
    main_section = forms.ModelChoiceField(queryset=Sections.objects.none(), label=u'Основная рубрика', required=True)
    business_lunch_price = forms.IntegerField(label=u'Минимальная стоимость бизнес-ланча', max_value=100000, min_value=0,
                                              widget=forms.TextInput, required=False)

    class Meta:
        model = Establishment
        fields = SectionFirmAdminForm.Meta.fields + (
            'main_section', 'alternative_name', 'contacts', 'is_new', 'wifi', 'dancing', 'karaoke', 'children_menu', 'terrace',
            'catering', 'business_lunch', 'cooking_class', 'breakfast', 'children_menu', 'cashless', 'live_music',
            'entertainment', 'banquet_hall', 'parking', 'facecontrol', 'types', 'bill', 'virtual_tour',
            'corporative', 'corporative_guest', 'corporative_price', 'corporative_description', 'barofest_description',
            'business_lunch_price', 'business_lunch_time', 'point', 'name_en', 'address_name_en', 'type_name',
            'type_name_en',
        )
        labels = {
            'business_lunch': u'Учитывать поля стоимости и времени бизнес-ланча',
        }

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):

        initial = initial or {}

        if instance:
            initial['guru_cause'] = instance.gurucause_set.all()

        super(EstablishmentAdminForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                                     empty_permitted, instance)

        sections_queryset = Sections.objects.filter(content_type=get_establishment_ct())
        self.fields['section'].queryset = sections_queryset
        self.fields['main_section'].queryset = sections_queryset

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = normalize_number(phone)
        return phone

    def save(self, *args, **kwargs):
        kwargs['commit'] = True
        instance = super(EstablishmentAdminForm, self).save(*args, **kwargs)
        cause_set = self.cleaned_data.get('guru_cause')

        instance.gurucause_set.through.objects.filter(establishment=instance, ).delete()
        for cause in cause_set:
            instance.gurucause_set.through.objects.create(establishment=instance, gurucause=cause)

        return instance


class AddressForm(forms.ModelForm):
    city_id = forms.ModelChoiceField(initial=1, queryset=Cities.objects.all(), label=u'Город',
                                     widget=forms.Select(attrs={'class': 'cit_selector'}))
    streetid = forms.ModelChoiceField(queryset=Streets.objects.all(), widget=forms.HiddenInput, required=False)
    streetname = AjaxTextField(url='/ref/search/', callback='StreetAutocompleteCallback', label=u'Улица',
                               required=False)

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        content_type = ContentType.objects.get_for_model(Streets)
        self.fields['streetname'].url = "/utils/objects/%s/" % content_type.pk  # TODO: reverse
        self.fields['streetname'].widget.url = "/utils/objects/%s/" % content_type.pk  # TODO: reverse

    class Meta:
        model = Address
        exclude = ('map', 'map_logo')


class GuruCauseAdminForm(forms.ModelForm):
    establishments = forms.ModelMultipleChoiceField(
        Establishment.objects.filter(visible=True).order_by('name'),
        label=u'заведения',
        widget=FilteredSelectMultiple(u'заведения', False))

    class Meta:
        model = GuruCause
        fields = '__all__'


class ArticleAdminForm(ArticleBaseAdminForm):
    """Форма редактирования статей раздела в админе"""

    mentions = EstablishmentAutocompleteMultipleField(label=u'Упоминания', required=False)

    class Meta(ArticleBaseAdminForm.Meta):
        model = Article
        fields = '__all__'


class ReviewAdminForm(ArticleAdminForm):
    """Форма редактирования резюме в админе"""

    establishment = EstablishmentAutocompleteField(label=u'Заведение', required=False)

    class Meta(ArticleAdminForm.Meta):
        model = Review
        fields = '__all__'


class EstablishmentSearchForm(forms.Form):

    BILL_CHOICES = (
        (Establishment.BILL_0_500, u'до 500'),
        (Establishment.BILL_1000_1500, u'1500'),
        (Establishment.BILL_1500_INF, u'от 1500'),
    )

    wifi = forms.BooleanField(label=u'Wi-Fi', required=False)
    dancing = forms.BooleanField(label=u'Танцпол', required=False)
    karaoke = forms.BooleanField(label=u'Караоке', required=False)
    live_music = forms.BooleanField(label=u'Живая музыка', required=False)
    children_room = forms.BooleanField(label=u'Детская комната', required=False)
    entertainment = forms.BooleanField(label=u'Развлекательная программа', required=False)
    banquet_hall = forms.BooleanField(label=u'Банкетный зал', required=False)
    business_lunch = forms.BooleanField(label=u'Бизнес-ланч', required=False)
    dinner = forms.BooleanField(label=u'Ужин', required=False)

    types = forms.ModelMultipleChoiceField(label=u'Кухня', queryset=Type.objects.all().order_by('position'),
                                           widget=forms.CheckboxSelectMultiple, required=False)

    bill = forms.MultipleChoiceField(label=u'Средний чек', choices=BILL_CHOICES, required=False,
                                     widget=BillCheckboxSelectMultiple)
    work_24_hour = forms.BooleanField(label=u'Круглосуточно', required=False)
    open_2_hour = forms.BooleanField(label=u'Будет открыто еще 2 часа', required=False)


class MenuAdminForm(forms.ModelForm):
    """Форма редактирования меню заваедения"""

    establishment = EstablishmentAutocompleteField(label=u'Заведение', required=True)

    class Meta:
        model = Menu
        fields = ('establishment', )


class CorporativeAdminForm(forms.ModelForm):
    """
    Форма редактирования корпоратива, участника барофеста и летней веранды
    Заведение выбирается удобным виджетом, а не огромным списком.
    """
    establishment = EstablishmentAutocompleteField(label=u'Заведение', required=True)


class AwardAdminForm(forms.ModelForm):
    """Форма редактирования наград"""

    establishment = EstablishmentAutocompleteField(label=u'Заведение', required=False)
    icon = forms.FileField(widget=AdminImagePreviewWidget(), required=False, label=u'Иконка')
