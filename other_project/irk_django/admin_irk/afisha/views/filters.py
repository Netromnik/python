# -*- coding: utf-8 -*-

import calendar
import datetime
import operator

from django.db.models import Q, Model
from django.db.models.query import QuerySet
from django.http import Http404

from irk.afisha.models import CurrentSession, EventType, Genre, Guide, Event, Prism
from irk.options.models import Site
from irk.utils.helpers import get_week_range

# Для фильтра по времени справочник с периодами
TIME_CHOICES = [
    ('morning', [[datetime.time(6, 0), datetime.time(12, 0)]]),
    ('day', [[datetime.time(12, 0), datetime.time(16, 0)]]),
    ('evening', [[datetime.time(16, 0), datetime.time(23, 0)],
                 [datetime.time(0, 0), datetime.time(6, 0)]])
]

TIME_CHOICES_NAMES = {
    'morning': u'утром',
    'day': u'днем',
    'evening': u'вечером',
}


class BaseFilter(object):
    """ Базовый фильтр событий
        Фильтры:
            - возвращают ORM filters
            - choices для рендеринга в шаблонах

        param - название параметра в исходных данных
        db_field - название поля в БД
        required - должен ли обрабатываться фильтр независимо есть он в данных или нет
        choice_model - Модель, объекты которой, должны возвращаться в качестве вариантов
    """

    def __init__(self, param, db_field=None, required=False, choice_model=None):
        self.param = param
        self.db_field = db_field or param
        self.required = required
        self.choice_model = choice_model

    def get_filters(self, value, view):
        """ Возвращает фильтры для ORM
            может фозвращать dict для filter(**dict)
            или Q для filter(Q)
        """
        if isinstance(value, Model):
            return {self.db_field: value}
        elif isinstance(value, (QuerySet, list)):
            return {'%s__in' % self.db_field: value}
        else:
            try:
                return {self.db_field: int(value)}
            except (ValueError, TypeError):
                return {}

    def get_choices(self, view, force_filter=None):
        """ Возвращает список возможных вариантов параметра.
            Зависит только от выбранного типа события.

            force_filter - необходим на странице конкретного события в фильтрах списка событий, чтобы отменить
            фильтрацию по конкретному событию (object)
        """
        today = datetime.datetime.now()
        queryset = CurrentSession.objects.filter(real_date__gte=today)

        if force_filter:
            if force_filter == 'event_type':
                queryset = queryset.filter(event_type=view.event_type)
        else:
            if hasattr(view, 'object') and view.object:
                queryset = queryset.filter(event_id=view.object.pk)
            elif hasattr(view, 'obj') and view.obj:
                queryset = queryset.filter(guide_id=view.obj.pk)
            elif hasattr(view, 'event_type') and view.event_type:
                queryset = queryset.filter(event_type=view.event_type)
            elif hasattr(view, 'index_types'):
                queryset = queryset.filter(event_type__in=view.index_types)

        queryset = queryset.values_list(self.db_field, flat=True).distinct()
        if self.choice_model:
            queryset = self.choice_model.objects.filter(id__in=queryset)
        return queryset


class TypeFilter(BaseFilter):
    """ Фильтр по типу события """

    def get_filters(self, value, view):
        """ Если не указан тип, то фильтруем по типу вьюхи """
        if not value:
            value = view.event_type if view.event_type else list(view.index_types.values_list('id', flat=True))
        return super(TypeFilter, self).get_filters(value, view)

    def get_choices(self, view, force_filter=None):
        return EventType.objects.filter(
            on_index=True,
            id__in=super(TypeFilter, self).get_choices(view, force_filter))


class SiteFilter(BaseFilter):
    """ Фильтр по разделу события """

    def get_filters(self, value, view):
        value = list(view.sites.values_list('id', flat=True))
        return super(SiteFilter, self).get_filters(value, view)


class WeekFilter(BaseFilter):
    """ Фильтр по дате показа """

    def get_filters(self, value, view):
        filters = {}
        if value:
            try:
                week_range = get_week_range(value)
            except (TypeError, ValueError):
                raise Http404()
            filters['date__range'] = [week_range[0], week_range[-1]]
        return filters


class DateFilter(BaseFilter):
    """ Фильтр по дате показа """

    def get_filters(self, value, view):
        filters = {}
        if value:
            # Дату можно передать как date
            # или ('week', date) - для фильтра по указанному месяцу
            # или ('month', date) - для фильтра по указанному месяцу

            extra_date = datetime.datetime.now()
            if type(value) is tuple:
                value, extra_date = value

            if type(value) is datetime.date:
                filters['date'] = value
            elif value == 'week':
                # Фильтр на неделю
                week_range = get_week_range(extra_date)
                filters['date__range'] = [week_range[0], week_range[-1]]
            elif value.startswith('week_'):
                # Фильтр на неделю по номеру недели
                try:
                    date = datetime.datetime.strptime(value[5:], '%Y%m%d')
                    week_range = get_week_range(date)
                except (TypeError, ValueError):
                    raise Http404()
                filters['date__range'] = [week_range[0], week_range[-1]]
            elif value == 'month':
                # Фильтр на текущий (по дате) месяц
                start_date = datetime.date(extra_date.year, extra_date.month, 1)
                month_days = calendar.monthrange(extra_date.year, extra_date.month)[1]
                end_date = datetime.date(extra_date.year, extra_date.month, month_days)
                filters['date__range'] = [start_date, end_date]
            elif value == '30day':
                # Фильтр на следующие 30 дней
                start_date = extra_date
                end_date = extra_date + datetime.timedelta(30)
                filters['date__range'] = [start_date, end_date]
            elif value == 'seven':
                # Фильтра на семь дней
                start_date = extra_date
                end_date = extra_date + datetime.timedelta(6)
                filters['date__range'] = [start_date, end_date]
            elif value == 'friday':
                # Фильтр на пятницу
                filters['date'] = get_week_range(extra_date)[4]
            elif value == 'saturday':
                # Фильтр на субботу
                filters['date'] = get_week_range(extra_date)[5]
            elif value == 'sunday':
                # Фильтр на вос
                filters['date'] = get_week_range(extra_date)[6]
            else:
                try:
                    filters['date'] = datetime.datetime.strptime(value, '%Y%m%d').date()
                except ValueError:
                    raise Http404()
        elif view.event_type and view.event_type.alias == 'cinema':
            # Для кино, если не указана  дата или период, делаем
            # фильтр по сегодняшней дате
            filters['date'] = datetime.date.today()

        return filters

    def get_choices(self, view, force_filter=None):
        choices = list(super(DateFilter, self).get_choices(view, force_filter).order_by('real_date'))

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(1)
        week_range = get_week_range(today)

        month_start_date = datetime.date(today.year, today.month, 1)
        month_days = calendar.monthrange(today.year, today.month)[1]
        month_end_date = datetime.date(today.year, today.month, month_days)
        has_current_month = bool(
            next((day for day in choices if month_start_date <= day <= month_end_date), False))

        result = {
            'today': today if today in choices else None,
            'tomorrow': tomorrow if tomorrow in choices else None,
            'week': 'week' if bool(set(choices) & set(week_range)) else None,
            'month': 'month' if has_current_month else None,
            'calendar': choices,
        }

        # Для ситуации с выставками, т.е. выводом расписания на 7 дней проверяем есть ли
        # расписание на след 7 дней и предыдущие
        if view:
            try:
                calendar_type, date = view.get_data().get('date')
            except (TypeError, ValueError):
                pass
            else:
                if calendar_type == 'seven':
                    next_seven = next((d for d in choices if d > date + datetime.timedelta(6)), None)
                    if next_seven:
                        weeks = (next_seven - date).days / 7
                        result['next_seven'] = date + datetime.timedelta(7 * weeks - 1)
                    rchoices = choices[:]
                    rchoices.reverse()
                    prev_seven = next((d for d in rchoices if d < date), None)
                    if prev_seven:
                        weeks = (date - prev_seven).days / 7 + 1
                        prev_seven = date - datetime.timedelta(7 * weeks - 1)
                        # Ссылки на прошедшие даты возвращают 404. Поэтому если начало предыдущей недели старше сегодня
                        # то за начальную дату берем сегодня.
                        result['prev_seven'] = today if prev_seven < today else prev_seven

        return result


class TimeFilter(BaseFilter):
    """ Фильтр по времени показа """

    def get_filters(self, value, view):
        choices = dict(TIME_CHOICES)
        if value and value in choices:
            by_time = [Q(time__range=time_range) for time_range in choices[value]]
            by_filter_time = [Q(filter_time__range=time_range) for time_range in choices[value]]
            return reduce(
                operator.__or__,
                by_time + by_filter_time)

    def get_choices(self, view, force_filter=None):
        result_choices = []
        time_chocies = list(super(TimeFilter, self).get_choices(view, force_filter).order_by('real_date'))
        for choice, values in TIME_CHOICES:
            for value in values:
                choice_items = [ch_time for ch_time in time_chocies if ch_time and value[0] <= ch_time <= value[1]]
                if choice_items:
                    result_choices.append((TIME_CHOICES_NAMES.get(choice), choice))
                    break
        return result_choices


date_filter = DateFilter(param='date')
week_filter = WeekFilter(param='week')
time_filter = TimeFilter(param='time')
type_filter = TypeFilter(param='type', db_field='event_type_id', required=True)
site_filter = SiteFilter(param='site', db_field='event__sites__id', required=True, choice_model=Site)
genre_filter = BaseFilter(param='genre', db_field='event__genre_id', choice_model=Genre)
event_filter = BaseFilter(param='event', db_field='event_id', choice_model=Event)
guide_filter = BaseFilter(param='guide', db_field='guide_id', choice_model=Guide)
is_3d_filter = BaseFilter(param='3d', db_field='is_3d')
prism_filter = BaseFilter(param='prism', db_field='event__prisms', choice_model=Prism)
