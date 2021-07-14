# -*- coding: utf-8 -*-

import datetime
import time

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms.models import BaseInlineFormSet

from irk.afisha.models import Guide, Event, Hall, EventGuide, Period, Sessions, Genre, EventType
from irk.phones.forms import SectionFirmAdminForm
from irk.utils.fields.select import AjaxTextField


class EventGuideFormSet(BaseInlineFormSet):
    eg_forms = {}

    def __init__(self, *args, **kwargs):
        # Сортировка привязок по алфавиту
        kwargs['queryset'] = kwargs['queryset'].order_by('guide__name')
        super(EventGuideFormSet, self).__init__(*args, **kwargs)
        for eg in kwargs['instance'].eventguide_set.all():
            prefix = "%s_%s" % (kwargs['prefix'], eg.pk)
            if self.data:
                self.eg_forms[eg.pk] = AddForm(self.data, prefix=prefix)
            else:
                self.eg_forms[eg.pk] = AddForm(prefix=prefix)


class GuideForm(forms.ModelForm):
    class Meta:
        model = Guide
        fields = '__all__'


class HallField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        try:
            return "%s/%s" % (obj.guide.name, obj.name)
        except:
            return obj.name


class EventGuideForm(forms.ModelForm):
    guide = forms.ModelChoiceField(
        queryset=Guide.objects.filter(visible=True).select_related('firms_ptr'),
        widget=forms.HiddenInput, label='', required=False)
    guide_name = AjaxTextField(
        url=None,
        callback='ObjectAutocompleteCallback', label=u"Гид")
    hall = HallField(
        queryset=Hall.objects.filter(guide__visible=True).select_related(
            'guide', 'guide__firms_ptr'),
        label='', required=False)

    def __init__(self, *args, **kwargs):
        super(EventGuideForm, self).__init__(*args, **kwargs)

        content_type = ContentType.objects.get_for_model(Guide)
        url = "%s?visible=1" % reverse('utils.views.get_objects',
                                       kwargs={'id': content_type.pk})
        self.fields['guide_name'].url = url
        self.fields['guide_name'].widget.url = url

        try:
            self.initial['guide_name'] = unicode(
                content_type.get_object_for_this_type(pk=self.initial['guide'])
            )
        except:  # TODO: перехват только необходимых исключений
            pass

    class Meta:
        models = EventGuide
        fields = '__all__'


class AddForm(forms.Form):
    dates = forms.RegexField(
        label=u'Даты', required=False, regex='[0-9\.\- \,]+',
        widget=forms.TextInput(attrs={'class': "ui-corner-all add_input"}))
    sessions = forms.RegexField(
        label=u'Сеансы', required=False, regex='[0-9\:\- ]+',
        widget=forms.TextInput(attrs={'class': "ui-corner-all add_input"}))
    price = forms.CharField(
        label=u'Цена', required=False,
        widget=forms.Textarea(attrs={'class': "ui-corner-all add_input add_textarea"}))

    def save(self, eg):
        if self.cleaned_data:
            try:
                eg = EventGuide.objects.get(pk=eg)
                for date in self.cleaned_data['dates']:
                    period = Period.objects.create(
                        event_guide=eg, start_date=date[0],
                        end_date=date[1], price=self.cleaned_data['price'])
                    for session in self.cleaned_data['sessions']:
                        Sessions.objects.create(period=period, time=session)
            except Exception:
                pass

    def clean(self):
        super(AddForm, self).clean()
        if not self.cleaned_data:
            return

        dates = self.cleaned_data.get('dates')
        if dates and type(dates) is not list:
            dates = []
            for date in dates.split(","):
                try:
                    date = date.strip().strip("-").strip(".")
                    period = date.split("-")
                    if len(period) == 2:
                        date_from, date_to = period[0].strip(), period[1].strip()
                    else:
                        date_from, date_to = period[0].strip(), None

                    date_from = datetime.datetime.strptime(date_from, "%d.%m.%y").date()
                    date_to = datetime.datetime.strptime(date_to, "%d.%m.%y").date() if date_to else date_from

                    dates.append((date_from, date_to))
                except:
                    pass

            self.cleaned_data['dates'] = dates
        sessions = self.cleaned_data.get('sessions')
        if sessions:
            sessions = []
            for session in sessions.split(","):
                try:
                    session = session.strip()
                    tm = time.strptime(session, "%H:%M")
                    sessions.append(datetime.time(*tm[3:6]))
                except:
                    pass
            self.cleaned_data['sessions'] = sessions
        return self.cleaned_data


class EventForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Event.objects.all(), widget=forms.HiddenInput, required=False)
    genre = forms.ModelChoiceField(queryset=Genre.objects.all().order_by('name'), label=u'Жанр', required=False)

    class Meta:
        model = Event
        fields = '__all__'


class CustomEventForm(forms.ModelForm):
    """Форма добавления событий для пользователей"""

    price = forms.CharField(label=u'Цена', required=False)
    place = forms.CharField(label=u'Место проведения', required=True)
    type = forms.ModelChoiceField(queryset=EventType.objects.filter(is_visible=True), required=True, label=u'Тип')
    organizer_contacts = forms.CharField(label=u'Контакты организатора', required=False)
    organizer_email = forms.CharField(label=u'E-mail организатора', required=False)
    is_commercial = forms.BooleanField(label=u'Коммерческое предложение', required=False)
    organizer = forms.CharField(label=u'Организатор', required=False)
    content = forms.CharField(label=u'Описание', required=False, widget=forms.Textarea)
    announcement_index_start_date = forms.DateField(input_formats=['%d.%m.%Y', '%d.%m.%y'],
                                                    label=u'Дата начала показа в ротации на главном слайдере',
                                                    widget=forms.TextInput(attrs={'placeholder': u'дд.мм.ГГГГ'}),
                                                    required=False)
    announcement_index_end_date = forms.DateField(input_formats=['%d.%m.%Y', '%d.%m.%y'],
                                                  label=u'Дата конца показа в ротации на главном слайдере',
                                                  widget=forms.TextInput(attrs={'placeholder': u'дд.мм.ГГГГ'}),
                                                  required=False)

    class Meta:
        model = Event
        fields = ('title', 'content', 'source_url', 'type', 'is_commercial', 'organizer', 'organizer_contacts',
                  'organizer_email', 'price', 'announcement_index_start_date', 'announcement_index_end_date',
                  'vk_url', 'fb_url', 'ok_url', 'inst_url', 'age_rating', 'wide_image')

    def clean(self):
        data = self.cleaned_data
        start_date = data.get('announcement_index_start_date')
        end_date = data.get('announcement_index_end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(u'Дата окончания должна быть позже даты начала')

        if (start_date or end_date) and (not start_date or not end_date):
            raise forms.ValidationError(u'Нужно указывать даты начала и окончания показа вместе')

    def clean_vk_url(self):
        url = self.cleaned_data.get('vk_url')
        if url and not url.startswith('http'):
            url = 'https://vk.com/{}'.format(url)
        return url

    def clean_fb_url(self):
        url = self.cleaned_data.get('fb_url')
        if url and not url.startswith('http'):
            url = 'https://www.facebook.com/{}'.format(url)
        return url

    def clean_ok_url(self):
        url = self.cleaned_data.get('ok_url')
        if url and not url.startswith('http'):
            url = 'https://ok.ru/{}'.format(url)
        return url

    def clean_inst_url(self):
        url = self.cleaned_data.get('inst_url')
        if url and not url.startswith('http'):
            url = 'https://www.instagram.com/{}'.format(url)
        return url

    def clean_announcement_index_start_date(self):
        date = self.cleaned_data.get('announcement_index_start_date')
        if date and date < datetime.date.today():
            raise forms.ValidationError(u'Только будущие даты')
        return date

    def clean_announcement_index_end_date(self):
        date = self.cleaned_data.get('announcement_index_end_date')
        if date and date < datetime.date.today():
            raise forms.ValidationError(u'Только будущие даты')
        return date

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        event = super(CustomEventForm, self).save(*args, **kwargs)
        if data['type']:
            Event.objects.filter(pk=event.pk).update(type=data['type'])
        if data['place']:
            Event.objects.filter(pk=event.pk).update(
                content=data['place'] + '\n\n' + event.content)
        return Event.objects.get(pk=event.pk)


class PeriodForm(forms.Form):
    date = forms.DateField(input_formats=['%d.%m.%Y', '%d.%m.%y'], label=u'Дата',
                           widget=forms.TextInput(attrs={'placeholder': u'дд.мм.ГГГГ'}), required=True)
    time = forms.TimeField(label=u'Время', widget=forms.TextInput(attrs={'placeholder': u'ЧЧ:ММ'}), required=True)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError(u'Обязательное поле')
        if date < datetime.date.today():
            raise forms.ValidationError(u'Только будущие события')
        return date


class GuideAdminForm(SectionFirmAdminForm):
    class Meta:
        fields = SectionFirmAdminForm.Meta.fields + ('article', 'event_type', 'title_short', 'map', 'price',
                                                     'price_description')
