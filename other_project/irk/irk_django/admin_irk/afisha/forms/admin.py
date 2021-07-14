# -*- coding: utf-8 -*-

import datetime
import itertools
import re
import time

from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.forms.models import BaseInlineFormSet
from django.forms.widgets import RadioSelect

from irk.afisha.forms.fields import (
    EventClearableAutocompleteField, EventForGuideAutocompleteField, GuideAutocompleteField,
    GuideClearableAutocompleteField, HallClearableAutocompleteField, ImdbIdAutocompleteField
)
from irk.afisha.helpers import get_price_for_period
from irk.afisha.models import Event, EventGuide, Genre, Guide, Hall, Period, Review, Sessions
from irk.news.forms import ArticleAdminForm as ArticleBaseAdminForm
from irk.utils.fields.file import AdminImagePreviewWidget
from irk.utils.fields.suggest import AjaxSuggestField

PERIOD_MAX_DAYS = 100


def parse(date):
    if date:
        formats = ["%d.%m.%Y", "%d.%m.%y", "%d-%m-%Y", ]
        for format in formats:
            try:
                return datetime.datetime.strptime(date.strip(), format).date()
            except ValueError:
                pass
    return None


class EventForm(forms.ModelForm):
    """Форма для редактирования события в админе"""

    genre = forms.ModelChoiceField(queryset=Genre.objects.all().order_by('name'), label=u'Жанр', required=False)
    imdb_id = ImdbIdAutocompleteField(label=u'Идентификатор в IMDB', required=False)
    wide_image = forms.ImageField(
        widget=AdminImagePreviewWidget(), required=False, label=u'Широкоформатная фотография',
        help_text=u'Размер: 960х454 пикселей'
    )

    class Meta:
        model = Event
        fields = '__all__'


class HallSelectWidget(forms.Select):
    def render(self, name, value, attrs=None, renderer=None):
        attrs['data-value'] = value
        return super(HallSelectWidget, self).render(
            name, value, attrs, renderer)

    def render_options(self, selected_choices):
        output = """
            <option value="" selected="selected">---------</option>
        """
        return output


class GuideForm(forms.ModelForm):
    class Meta:
        model = Guide
        fields = []


class EventGuideSessionFormMixin(forms.ModelForm):
    def clean(self):
        data = self.cleaned_data
        periods = {}
        form_index = self.prefix.replace('eventguide_set-', '')
        for k, v in self.data.items():
            if k.startswith("period-%s" % form_index):
                key = k.replace("period-%s-" % form_index, "")
                try:
                    key_id, key_name = key.split("-")
                except ValueError:
                    continue
                if not key_id in periods:
                    periods[key_id] = {}
                periods[key_id][key_name] = v
        data['periods'] = periods.values()

        for period in data['periods']:
            date_periods = self.parse_dates(period.get('date'))
            for date in list(itertools.chain(*date_periods)):
                if not isinstance(date, datetime.date):
                    raise forms.ValidationError(
                        u'Неверный формат даты в периоде расписания')
            for start_date, end_date in date_periods:
                if (end_date - start_date) > datetime.timedelta(PERIOD_MAX_DAYS):
                    raise forms.ValidationError(
                        u'Период должен быть не больше %d дней. <<%s>> - <<%s>>' %
                        (PERIOD_MAX_DAYS, start_date, end_date)
                    )
        return data

    def parse_dates(self, dates):
        date_periods = []
        if dates:
            for period in dates.split(","):
                period = period.strip().strip("-").strip(".")
                dates = period.split("-")
                if len(dates) == 1:
                    dates.append(dates[0])
                date_periods.append(map(parse, dates))
        return date_periods

    def parse_sessions(self, sessions):
        """Парсинг строки с временем проведения событий

        >>> self.parse_sessions('10:00, 12:00,13:00 13:00 16:00')
        datetime.time(10, 0), datetime.time(12, 0), datetime.time(13, 0), datetime.time(14, 0)
        """

        sessions = re.split("[\ ,]", sessions.strip())
        sessions = filter(bool, sessions)
        try:
            sessions = map(
                lambda s: time.strptime(s.strip(), "%H:%M"), sessions
            )
        except ValueError:
            return []
        sessions = map(lambda t: datetime.time(*t[3:6]), sessions)

        return list(set(sessions))

    def parse_duration(self, duration):
        duration = duration.strip()
        if duration:
            try:
                t = time.strptime(duration, "%H:%M")
                return datetime.time(*t[3:6])
            except ValueError:
                pass

    def save_sessions(self, obj):
        """ Сохраняем периоды и сессии """

        if not obj or not obj.pk:
            return

        periods = self.cleaned_data.get('periods', [])
        saved = []
        for period in periods:
            saved_periods = []
            date_periods = self.parse_dates(period.get('date'))
            sessions = self.parse_sessions(period.get('sessions'))
            try:
                pk = int(period.get('id'))
            except (TypeError, ValueError):
                pk = None
            ids = [pk] + [None for i in range(len(date_periods) - 1)]
            date_periods = zip(date_periods, ids)
            for dates, pk in date_periods:
                try:
                    period_o = Period.objects.get(pk=pk, event_guide=obj)
                except Period.DoesNotExist:
                    period_o = Period(event_guide=obj)
                period_o.price = period.get('price')
                period_o.duration = self.parse_duration(period.get('duration'))
                period_o.is_3d = period.get('is_3d') == '1'
                period_o.start_date, period_o.end_date = dates
                period_o.save()
                sessions_saved = []
                for session in sessions:
                    s, _ = Sessions.objects.get_or_create(
                        period=period_o,
                        time=session,
                        price=get_price_for_period(period_o),
                    )
                    sessions_saved.append(s.pk)
                period_o.sessions_set.exclude(pk__in=sessions_saved).delete()
                saved_periods.append(period_o.pk)
            saved += saved_periods
        obj.period_set.exclude(pk__in=saved).delete()


class EventGuideForm(EventGuideSessionFormMixin):
    guide = GuideAutocompleteField(label=u'Место')
    hall = forms.ModelChoiceField(
        label=u'Зал',
        queryset=Hall.objects.all(),
        widget=HallSelectWidget,
        required=False,
    )

    class Meta:
        model = EventGuide
        fields = ('hall',)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super(EventGuideForm, self).__init__(*args, **kwargs)
        if instance:
            self.initial['guide'] = instance.guide if instance.guide_id else instance.guide_name

    def clean(self):
        data = super(EventGuideForm, self).clean()
        establishment = data.get('guide')
        if establishment and type(establishment) in [str, unicode]:
            data['guide_name'] = establishment
            data['guide'] = None
        elif establishment:
            data['guide_name'] = unicode(establishment)
            data['guide'] = establishment
        return data

    def save(self, *args, **kwargs):
        obj = super(EventGuideForm, self).save(*args, **kwargs)
        obj.guide = self.cleaned_data.get('guide')
        obj.guide_name = self.cleaned_data.get('guide_name')
        if kwargs.get('commit', ):
            obj.save()
        return obj


class GuideEventGuideForm(EventGuideSessionFormMixin):
    event = EventForGuideAutocompleteField(label=u'Событие')
    hall = forms.ModelChoiceField(
        label=u'Зал',
        queryset=Hall.objects.all(),
        widget=HallSelectWidget,
        required=False,
    )

    class Meta:
        model = EventGuide
        fields = ('hall', )

    def clean_event(self):
        event = self.cleaned_data['event']
        if not isinstance(event, Event):
            raise forms.ValidationError(u'Введите существующее событие')

        return event


class PaginatedFormSet(BaseInlineFormSet):
    """ Для вывода прошедших привязок с пагинатором """

    def total_form_count(self):
        if self.is_all_bindings == 1:
            return len(self.get_queryset())
        else:
            return super(PaginatedFormSet, self).total_form_count()

    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            super(PaginatedFormSet, self).get_queryset()
            if self.is_all_bindings == 1:
                paginator = Paginator(self._queryset, 10)
                try:
                    page = paginator.page(self.page)
                except PageNotAnInteger:
                    page = paginator.page(1)
                except EmptyPage:
                    page = paginator.page(paginator.num_pages)

                self._queryset = page.object_list
                self.paginator = page
        return self._queryset


class ReviewAdminForm(ArticleBaseAdminForm):
    """Форма редактирования статей раздела в админе"""

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super(ReviewAdminForm, self).__init__(*args, **kwargs)
        self.fields['event'] = AjaxSuggestField(Event, label=u'Событие', allow_non_fk=True)
        if instance:
            self.initial['event'] = (
                instance.event_id, unicode(instance.event))

    class Meta(ArticleBaseAdminForm.Meta):
        model = Review
        fields = '__all__'


class TicketEventChangeListAdminForm(forms.ModelForm):
    """Форма админки для связывания событий kassy.ru с нашими"""

    event = EventClearableAutocompleteField(label=u'Событие', required=False)


class TicketBuildingChangeListAdminForm(forms.ModelForm):
    """Форма админки для связывания учреждений kassy.ru с нашими"""

    guide = GuideClearableAutocompleteField(label=u'Заведение гида', required=False)


class TicketHallChangeListAdminForm(forms.ModelForm):
    """Форма админки для связывания залов rambler.kassa с нашими"""

    hall = HallClearableAutocompleteField(label=u'Зал', required=False)


class AnnouncementAdminInlineForm(forms.ModelForm):
    """Форма для инлайнового редактирования анонсов в админке"""

    def clean(self):
        start = self.cleaned_data.get('start')
        end = self.cleaned_data.get('end')

        if not start or not end:
            raise forms.ValidationError(u'Не указаны начальная и конечная даты анонса')

        if start > end:
            raise forms.ValidationError(u'Неверно заданы даты')

        return self.cleaned_data


class PrismAdminForm(forms.ModelForm):
    """Форма редактирования призм"""

    icon = forms.FileField(widget=AdminImagePreviewWidget(), required=False, label=u'Иконка')
