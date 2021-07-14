# -*- coding: utf-8 -*-

import datetime
import random
import calendar

from django.apps import apps
from django.db.models import Min

from dateutil import relativedelta

from irk.afisha import settings as app_settings
from irk.afisha.models import Event, Announcement, EventType
from irk.news.models import BaseMaterial
from irk.options.models import Site
from irk.utils.views.mixins import PaginateMixin


class ExtraAnnouncementsController(PaginateMixin):
    """Контроллер для получения дополнительных анонсов"""

    def __init__(self, event_type=None, date=None):
        self._event_type = event_type
        self._date = date or datetime.date.today()

    def get_announce_events(self, start_index, limit):
        """
        Получить порцию событий с анонсами

        :param int start_index: индекс начала
        :param int limit: количество возвращаемых объектов
        :return tuple: список объектов и информация о странице
        """

        event_list = self._get_events()
        object_list, page_info = self._paginate(event_list, start_index, limit)

        return object_list, page_info

    def _get_events(self):
        """Вернуть события для которых есть анонсы"""

        filters = {}
        if self._event_type:
            filters.update({
                'event__type': self._event_type,
                'place': Announcement.PLACE_AFISHA_TYPE_PAGE,
            })

        event_ids = list(
            Announcement.objects.filter(**filters).active().values_list('event', flat=True)
        )
        events = Event.objects \
            .filter(id__in=event_ids, is_hidden=False) \
            .annotate(real_date=Min('currentsession__real_date')) \
            .order_by('real_date')

        return events


class ExtraEventController(PaginateMixin):
    """Контроллер для дополнительных событий"""

    event_type = None

    def __init__(self, event=None):
        self._event = event

    def get_events(self, start_index, limit):
        """
        Получить порцию событий

        :param int start_index: индекс начала
        :param int limit: количество возвращаемых объектов
        :return tuple: список объектов и информация о странице
        """

        event_list = self._get_events()
        object_list, page_info = self._paginate(event_list, start_index, limit)

        return object_list, page_info

    def apply_filters(self, events):
        return events

    def _get_events(self):

        events = Event.objects.filter(is_hidden=False)
        if self.event_type:
            events = events.filter(type=self.event_type)

        if self._event:
            events = events.exclude(pk=self._event.pk)

        events = self.apply_filters(events)
        events = events.annotate(real_date=Min('currentsession__real_date'))\
            .order_by('real_date')

        # Сохраняем расписание сеансов для событий
        for event in events:
            current_sessions = event.currentsession_set \
                .filter(real_date__gte=datetime.date.today()) \
                .order_by('real_date')
            for session in current_sessions:
                event.schedule.append(session)

        return events


class ExtraCinemaController(ExtraEventController):
    """Контроллер для получения фильмов на ближайшую неделю"""

    def __init__(self, event=None):
        super(ExtraCinemaController, self).__init__(event)
        self.event_type = EventType.objects.get(alias='cinema')

    def apply_filters(self, events):
        now = datetime.datetime.now()
        return events.filter(currentsession__real_date__gte=now,
                             currentsession__real_date__lte=now + datetime.timedelta(7))


class ExtraCultureController(ExtraEventController):
    """Контроллер для получения спектаклей на следующий месяц"""

    def __init__(self, event=None):
        super(ExtraCultureController, self).__init__(event)
        self.event_type = EventType.objects.get(alias='culture')

    def apply_filters(self, events):
        next_month = datetime.datetime.today() + relativedelta.relativedelta(months=1)
        _, next_month_days_count = calendar.monthrange(next_month.year, next_month.month)

        start_next_month = datetime.datetime(next_month.year, next_month.month, 1)
        end_next_month = datetime.datetime(next_month.year, next_month.month, next_month_days_count)

        return events.filter(currentsession__real_date__gte=start_next_month,
                             currentsession__real_date__lte=end_next_month)


class ExtraMaterialController(PaginateMixin):
    """Контроллер для получения лонгридов"""

    def get_materials(self, start_index, limit):
        """
        Получить порцию лонгридов афишы

        :param int start_index: индекс начала
        :param int limit: количество возвращаемых объектов
        :return tuple: список объектов и информация о странице
        """

        material_list = self._get_materials()
        materials, page_info = self._paginate(material_list, start_index, limit)
        object_list = [m.cast() for m in materials]

        return object_list, page_info

    def _get_materials(self):
        afisha_site = Site.objects.get(slugs='afisha')
        materials = BaseMaterial.longread_objects.filter(sites=afisha_site).exclude(is_advertising=True) \
            .filter(is_hidden=False).order_by('-stamp', '-pk')
        return materials


class SliderAnnouncementsController(object):
    """Контроллер для списка анонсов в слайдере"""

    # максимальное количество всех объектов
    LIMIT = 10

    def __init__(self, event_type=None, show_hidden=False):
        # События могут выводится по типу
        self._event_type = event_type
        # Отображать скрытые
        self._show_hidden = show_hidden

    def get_announcements(self):
        """Получить анонсируемые объекты"""

        # Если есть тип событий, то отображаем только события данного типа
        if self._event_type:
            events = self._get_events()
            random.shuffle(events)
            return events[:self.LIMIT]

        events = self._get_events()
        materials = self._get_materials()

        result_list = events + materials
        random.shuffle(result_list)

        return result_list[:self.LIMIT]

    def _get_events(self):
        """Получить события"""

        if self._event_type:
            filters = {
                'event__type': self._event_type,
            }
            place = Announcement.PLACE_AFISHA_TYPE_PAGE
        else:
            filters = {}
            place = Announcement.PLACE_AFISHA_INDEX

        if not self._show_hidden:
            filters['event__is_hidden'] = False

        event_ids = list(Announcement.objects.for_place(place).filter(**filters).active()
                         .values_list('event', flat=True))
        events = list(Event.objects.filter(id__in=event_ids)[:self.LIMIT])

        # Сохраняем расписание сеансов для событий
        for event in events:
            current_sessions = event.currentsession_set \
                .filter(real_date__gte=datetime.date.today()) \
                .order_by('real_date')
            for session in current_sessions:
                event.schedule.append(session)

        self._mark(events, 'event')

        return events

    def _get_materials(self):
        """Получить материалы"""

        materials = []

        filters = {
            'is_announce': True
        }

        if not self._show_hidden:
            filters['is_hidden'] = False

        materials_classes = self._get_material_classes()
        for material_class in materials_classes:
            materials.extend(material_class.objects.filter(**filters)[:self.LIMIT])

        materials = sorted(materials, key=lambda m: m.get_sorting_key(), reverse=True)[:self.LIMIT]

        self._mark(materials, 'material')

        return materials

    def _get_material_classes(self):
        """Получить классы материалов, которые можно отображать в слайдере"""

        models = []
        for class_name in app_settings.SLIDER_MATERIAL_CLASSES:
            models.append(apps.get_model('afisha', class_name))

        return models

    def _mark(self, object_list, announce_type):
        """
        Пометить объекты, что они принадлежат определенному типу

        :param list object_list: список объектов
        :param str announce_type: описание типа
        """

        for item in object_list:
            item.announce_type = announce_type
