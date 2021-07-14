# -*- coding: UTF-8 -*-
from urlparse import urlparse

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, ModelChoiceField, HiddenInput, Select
from django.forms.fields import CharField
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.urls import reverse_lazy

from irk.map.fields import PointField
from irk.map.models import Cities, Streets
from irk.phones import models as phones
from irk.phones.models import Firms, Worktime, Address
from irk.profiles.forms.fields import UserAutocompleteField
from irk.utils.fields.select import AjaxTextField, MultiAjaxTextField
from irk.utils.settings import WEEKDAYS
from irk.utils.helpers import get_cities

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


class SearchForm(Form):
    q = CharField(max_length=100)


def save_instance(form, instance, fields=None, fail_message='saved', commit=True, exclude=None):
    """
    Saves bound Form ``form``'s cleaned_data into model instance ``instance``.

    If commit=True, then the changes to ``instance`` will be saved to the
    database. Returns ``instance``.
    """
    from django.db import models
    opts = instance._meta
    if form.errors:
        raise ValueError("The %s could not be %s because the data didn't"
                         " validate." % (opts.object_name, fail_message))
    cleaned_data = form.cleaned_data
    file_field_list = []
    for f in opts.fields:
        if not f.editable or isinstance(f, models.AutoField) \
                or not f.name in cleaned_data:
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        # OneToOneField doesn't allow assignment of None. Guard against that
        # instead of allowing it and throwing an error.
        if isinstance(f, models.OneToOneField) and cleaned_data[f.name] is None:
            continue
        # Defer saving file-type fields until after the other fields, so a
        # callable upload_to can use the values from other fields.
        if isinstance(f, models.FileField):
            file_field_list.append(f)
        else:
            f.save_form_data(instance, cleaned_data[f.name])

    for f in file_field_list:
        f.save_form_data(instance, cleaned_data[f.name])

    # Wrap up the saving of m2m data as a function.
    def save_m2m():
        opts = instance._meta
        cleaned_data = form.cleaned_data
        for f in opts.many_to_many:
            if fields and f.name not in fields:
                continue
            if f.name in cleaned_data:
                phones.Firms._meta.get_field_by_name('section')[0].rel.through.filter(firms=instance).delete()
                for section in cleaned_data[f.name]:
                    map = phones.Firms._meta.get_field_by_name('section')[0].rel.through(section=section, firm=instance)
                    map.save()
    if commit:
        # If we are committing, save the instance and the m2m data immediately.
        instance.save()
        save_m2m()
    else:
        # We're not committing. Add a method to the form to allow deferred
        # saving of m2m data.
        form.save_m2m = save_m2m
    return instance


class FirmForm(forms.ModelForm):
    section = MultiAjaxTextField(queryset=phones.Sections.objects.all(), required=False,
                                 url=reverse_lazy('utils:sections_suggest'), callback='Autocomplete', amount=3,
                                 label=u'Рубрики')
    # TODO можно удалить при переезде на django 1.7
    mail = forms.EmailField(label=u'E-mail', error_messages={'invalid': u'Введите корректный E-mail.'}, required=False)

    class Meta:
        model = phones.Firms
        fields = ('name', 'url', 'mail', 'description', 'logo', 'section',)


class FirmAdminForm(forms.ModelForm):
    """Форма базовой фирмы в админке"""

    user = UserAutocompleteField(label=u'Пользователь', required=False)
    section = MultiAjaxTextField(queryset=phones.Sections.objects.all(), required=False,
                                 url=reverse_lazy('utils:sections_suggest'), callback='AutocompleteCallback', amount=10,
                                 label=u'Рубрики', new=True)

    class Meta:
        model = phones.Firms
        fields = ('hide_comments', 'disable_comments', 'user', 'name', 'alternative_name', 'url', 'mail', 'description',
                  'logo', 'visible', 'section', 'wide_image')

    def clean_url(self):
        if self.cleaned_data["url"]:
            url = urlparse(self.cleaned_data["url"], scheme='http')
            return '%s://%s%s' % (url.scheme, url.netloc, url.path)
        return ''

    def save_m2m(self):
        pass


class SectionFirmAdminForm(FirmAdminForm):
    """Базовая форма админки для всех моделей-наследников `phones.models.SectionFirm'"""

    firms_ptr = forms.ModelChoiceField(queryset=Firms.objects.all(), widget=forms.HiddenInput, required=False)

    class Meta:
        model = phones.SectionFirm
        # Нам нужен скрытый firms_ptr, чтобы заполнять модели-наследники
        fields = FirmAdminForm.Meta.fields + ('firms_ptr',)


class InlineFormSet(BaseInlineFormSet):
    def __init__(self, data=None, files=None, instance=None, save_as_new=False, prefix=None):
        super(InlineFormSet, self).__init__(data, files, instance, save_as_new, prefix)

    def clean(self):
        super(InlineFormSet, self).clean()

        for form in self.forms:
            if form.has_changed() or form.instance.pk:
                break
        else:
            pass

        show = False
        for form in reversed(self.forms):
            if form.has_changed() or form.instance.pk:
                show = True

            if show:
                setattr(form, 'show', True)


class AddressForm(ModelForm):
    city_id = ModelChoiceField(initial=1, queryset=Cities.objects.all(), required=True, label=u'Город',
                               widget=Select(attrs={'class': 'cit_selector'}))
    streetid = ModelChoiceField(queryset=Streets.objects.all(), widget=HiddenInput, required=False)
    streetname = AjaxTextField(url="/ref/search/", callback='StreetAutocompleteCallback',
                               label=u"Улица", required=False)

    class Meta:
        models = phones.Address
        exclude = ('map', 'name')

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        content_type = ContentType.objects.get_for_model(Streets)
        self.fields['streetname'].url = "/utils/objects/%s/" % content_type.pk
        self.fields['streetname'].widget.url = "/utils/objects/%s/" % content_type.pk

        if self.initial.get('streetid'):
            self.initial['streetname'] = Streets.objects.get(pk=self.initial['streetid']).name


AddressFormSet = inlineformset_factory(phones.Firms, phones.Address, formset=InlineFormSet,
                                       form=AddressForm, extra=1, max_num=10, fields='__all__')


class WorkTimeInput(forms.TimeInput):
    """Текстовое поля для ввода времени в формате %H:%M"""

    def __init__(self):
        super(WorkTimeInput, self).__init__(attrs={'type': 'time'}, format='%H:%M')


class AddressObedForm(ModelForm):
    city_id = forms.ModelChoiceField(initial=1, queryset=None, empty_label=None, label=u'Город', required=True,
                                     widget=Select(attrs={'class': 'cit_selector'}))
    name = forms.CharField(label=u'Адрес', required=False)
    point = PointField(label=u'Координата', widget=forms.HiddenInput(), required=False)

    day0_start = forms.TimeField(label=u'ПН. начало', required=False, widget=WorkTimeInput)
    day0_end = forms.TimeField(label=u'ПН. конец', required=False, widget=WorkTimeInput)
    day1_start = forms.TimeField(label=u'ВТ. начало', required=False, widget=WorkTimeInput)
    day1_end = forms.TimeField(label=u'ВТ. конец', required=False, widget=WorkTimeInput)
    day2_start = forms.TimeField(label=u'СР. начало', required=False, widget=WorkTimeInput)
    day2_end = forms.TimeField(label=u'СР. конец', required=False, widget=WorkTimeInput)
    day3_start = forms.TimeField(label=u'ЧТ. начало', required=False, widget=WorkTimeInput)
    day3_end = forms.TimeField(label=u'ЧТ. конец', required=False, widget=WorkTimeInput)
    day4_start = forms.TimeField(label=u'ПТ. начало', required=False, widget=WorkTimeInput)
    day4_end = forms.TimeField(label=u'ПТ. конец', required=False, widget=WorkTimeInput)
    day5_start = forms.TimeField(label=u'СБ. начало', required=False, widget=WorkTimeInput)
    day5_end = forms.TimeField(label=u'СБ. конец', required=False, widget=WorkTimeInput)
    day6_start = forms.TimeField(label=u'ВС. начало', required=False, widget=WorkTimeInput)
    day6_end = forms.TimeField(label=u'ВС. конец', required=False, widget=WorkTimeInput)

    class Meta:
        models = Address
        fields = ('city_id', 'name', 'point', 'phones', 'twenty_four_hour', 'day0_start', 'day0_end', 'day1_start',
                  'day1_end', 'day2_start', 'day2_end', 'day3_start', 'day3_end', 'day4_start', 'day4_end',
                  'day5_start', 'day5_end', 'day6_start', 'day6_end')

    def __init__(self, *args, **kwargs):
        super(AddressObedForm, self).__init__(*args, **kwargs)
        self.fields['city_id'].queryset = get_cities('obed')

        if self.instance:
            worktimes = Worktime.objects.filter(address=self.instance.pk)
            for worktime in worktimes:
                self.initial['day{}_start'.format(worktime.weekday)] = worktime.start_time
                self.initial['day{}_end'.format(worktime.weekday)] = worktime.end_time

    def clean(self):
        cleaned_data = super(AddressObedForm, self).clean()

        # Валидация времени работы.
        for weekday in WEEKDAYS.keys():
            start_time_key = 'day{}_start'.format(weekday)
            end_time_key = 'day{}_end'.format(weekday)
            start_time = cleaned_data.get(start_time_key)
            end_time = cleaned_data.get(end_time_key)
            if start_time is not None and end_time is None:
                errors = self._errors.get(end_time_key, [])
                errors.append(u'Не указано время окончания работы')
                self._errors[end_time_key] = self.error_class(errors)
                cleaned_data.pop(end_time_key, None)
            if end_time is not None and start_time is None:
                errors = self._errors.get(start_time_key, [])
                errors.append(u'Не указано время начала работы')
                self._errors[start_time_key] = self.error_class(errors)
                cleaned_data.pop(start_time_key, None)

        return cleaned_data

    def save(self, commit=True):
        address = super(AddressObedForm, self).save(commit=True)
        worktimes = {w.weekday: w for w in address.address_worktimes.all()}

        for weekday in WEEKDAYS.keys():
            start_time_key = 'day{}_start'.format(weekday)
            end_time_key = 'day{}_end'.format(weekday)
            try:
                start_time = self.cleaned_data[start_time_key]
                end_time = self.cleaned_data[end_time_key]
            except KeyError:
                continue

            if start_time is not None and end_time is not None:
                worktime = worktimes.get(weekday, Worktime(weekday=weekday))
                worktime.start_time = start_time
                worktime.end_time = end_time
                worktime.address = address
                worktime.save()
            elif start_time is None and end_time is None:
                if weekday in worktimes:
                    worktimes[weekday].delete()

        return address


AddressObedFormSet = inlineformset_factory(phones.Firms, phones.Address, formset=InlineFormSet,
                                           form=AddressObedForm, extra=1, max_num=1, fields='__all__')


class AddressFormset(inlineformset_factory(phones.Firms, phones.Address, fields='__all__')):
    def __init__(self, *args, **kwargs):
        super(AddressFormset, self).__init__(*args, **kwargs)
        self.can_delete = True


class AddressWorktimeWithDinnerForm(AddressObedForm):
    city_id = forms.ModelChoiceField(initial=1, queryset=None, empty_label=None, label=u'Город', required=True,
                                     widget=Select(attrs={'class': 'cit_selector'}))

    day0_dinner_start = forms.TimeField(required=False, widget=WorkTimeInput)
    day0_dinner_end = forms.TimeField(required=False, widget=WorkTimeInput)
    day1_dinner_start = forms.TimeField(required=False, widget=WorkTimeInput)
    day1_dinner_end = forms.TimeField(required=False, widget=WorkTimeInput)
    day2_dinner_start = forms.TimeField(required=False, widget=WorkTimeInput)
    day2_dinner_end = forms.TimeField(required=False, widget=WorkTimeInput)
    day3_dinner_start = forms.TimeField(required=False, widget=WorkTimeInput)
    day3_dinner_end = forms.TimeField(required=False, widget=WorkTimeInput)
    day4_dinner_start = forms.TimeField(required=False, widget=WorkTimeInput)
    day4_dinner_end = forms.TimeField(required=False, widget=WorkTimeInput)
    day5_dinner_start = forms.TimeField(required=False, widget=WorkTimeInput)
    day5_dinner_end = forms.TimeField(required=False, widget=WorkTimeInput)
    day6_dinner_start = forms.TimeField(required=False, widget=WorkTimeInput)
    day6_dinner_end = forms.TimeField(required=False, widget=WorkTimeInput)

    class Meta:
        model = Address
        fields = AddressObedForm.Meta.fields + (
            'day0_dinner_start', 'day0_dinner_end', 'day1_dinner_start', 'day1_dinner_end', 'day2_dinner_start',
            'day2_dinner_end', 'day3_dinner_start', 'day3_dinner_end', 'day4_dinner_start', 'day4_dinner_end',
            'day5_dinner_start', 'day5_dinner_end', 'day6_dinner_start', 'day6_dinner_end',
        )

    def __init__(self, *args, **kwargs):
        super(AddressWorktimeWithDinnerForm, self).__init__(*args, **kwargs)

        self['city_id'].queryset = get_cities('currency')  # lazy qs

        if self.instance:
            worktimes = Worktime.objects.filter(address=self.instance.pk)
            for worktime in worktimes:
                self.initial['day{}_dinner_start'.format(worktime.weekday)] = worktime.dinner_start_time
                self.initial['day{}_dinner_end'.format(worktime.weekday)] = worktime.dinner_end_time

    def clean(self):
        cleaned_data = super(AddressWorktimeWithDinnerForm, self).clean()

        # Валидация обеда для времени работы.
        for weekday in WEEKDAYS.keys():
            dinner_start_time_key = 'day{}_dinner_start'.format(weekday)
            dinner_end_time_key = 'day{}_dinner_end'.format(weekday)
            dinner_start_time = cleaned_data.get(dinner_start_time_key)
            dinner_end_time = cleaned_data.get(dinner_end_time_key)
            if dinner_start_time is not None and dinner_end_time is None:
                errors = self._errors.get(dinner_end_time_key, [])
                errors.append(u'Не указано время окончания обеда')
                self._errors[dinner_end_time_key] = self.error_class(errors)
                cleaned_data.pop(dinner_end_time_key, None)
            if dinner_end_time is not None and dinner_start_time is None:
                errors = self._errors.get(dinner_start_time_key, [])
                errors.append(u'Не указано время начала обеда')
                self._errors[dinner_start_time_key] = self.error_class(errors)
                cleaned_data.pop(dinner_start_time_key, None)

        return cleaned_data

    def save(self, commit=True):
        address = super(AddressWorktimeWithDinnerForm, self).save(commit=True)
        worktimes = {w.weekday: w for w in address.address_worktimes.all()}

        # Сохраняем время обеда
        for weekday in WEEKDAYS.keys():
            dinner_start_time_key = 'day{}_dinner_start'.format(weekday)
            dinner_end_time_key = 'day{}_dinner_end'.format(weekday)
            try:
                dinner_start_time = self.cleaned_data[dinner_start_time_key]
                dinner_end_time = self.cleaned_data[dinner_end_time_key]
            except KeyError:
                continue

            worktime = worktimes.get(weekday)
            if not worktime:
                continue
            worktime.dinner_start_time = dinner_start_time
            worktime.dinner_end_time = dinner_end_time
            address.address_worktimes.add(worktime)

        return address


AddressWorktimeWithDinnerFormSet = inlineformset_factory(
    phones.Firms, phones.Address, formset=InlineFormSet, form=AddressWorktimeWithDinnerForm, extra=1, max_num=1,
    fields='__all__',
)


class AddressAdminInlineForm(forms.ModelForm):
    """Инлайн-форма для адресов фирм"""

    streetid = forms.ModelChoiceField(queryset=Streets.objects.all(), widget=forms.HiddenInput,
                                      label=u'', required=False)
    # TODO: reverse_lazy
    streetname = AjaxTextField(url='/utils/streets/', callback='StreetCallback',
                               min_length=3, max_length=255, required=False, label=u'Улица')

    class Meta:
        model = phones.Address
        fields = ('name', 'firm_id', 'city_id', 'streetname', 'location', 'officenumber',
                  'descr', 'streetid', 'phones', 'worktime')

    def __init__(self, *args, **kwargs):
        super(AddressAdminInlineForm, self).__init__(*args, **kwargs)
        if self.initial.get('streetid'):
            self.initial['streetname'] = Streets.objects.get(pk=self.initial['streetid']).name


class SectionAdminForm(ModelForm):

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:

            count = phones.Sections.objects.filter(slug=slug).exclude(pk=self.instance.pk).count()
            if count > 0:
                raise ValidationError(u'Уже есть рубрика с таким алисом')
        return slug

    class Meta:
        model = phones.Sections
        fields = '__all__'
