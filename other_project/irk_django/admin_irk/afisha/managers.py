# -*- coding: UTF-8 -*-

import datetime

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

from irk.utils.decorators import deprecated


class PeriodManager(models.Manager):
    def for_date(self, date):
        qs = self.get_queryset().filter(start_date__lte=date, end_date__gte=date)
        for period in qs:
            setattr(period, "current_date", date)
        return qs

    def defaults(self):
        now = datetime.datetime.now()
        start = (now.date() - self.start()).days
        start = start > 0 and start or 0
        return [start, self.days()]

    def start(self):
        return self.get_queryset().all().order_by('start_date').values_list("start_date", flat=True)[0]

    def end(self):
        return self.get_queryset().all().order_by('-end_date').values_list("end_date", flat=True)[0]

    def days(self):
        try:
            diff = self.end() - self.start()
            return diff.days
        except Exception, e:
            pass
        return ''

    def active(self):
        return self.get_queryset()

    def admin_all(self):
        return self.get_queryset().order_by("-end_date")


class SessionsManager(models.Manager):
    def expected(self):
        time = datetime.datetime.now().time()
        return self.get_queryset().filter(time__gt=time)

    def __unicode__(self):
        return "&nbsp;&nbsp;&nbsp;".join(
            [session.strftime("%H:%M") for session in self.get_queryset().values_list("time", flat=True)])

    def repr(self):
        return ', '.join([session.strftime("%H:%M") for session in self.get_queryset().values_list("time", flat=True)])


class EventsQuerySet(QuerySet):
    filter_info = {}

    def __setitem__(self, attr, value):
        self.filter_info[attr] = value

        @deprecated
        def iterator(self):
            """Какой-то старый legacy код
            Непонятно, зачем нужен.

            # TODO: выяснить и удалить
            """

            for obj in super(EventsQuerySet, self).iterator():
                for key in self.filter_info:
                    setattr(obj, key, self.filter_info[key])
                yield obj


class EventManager(models.Manager):
    def get_queryset(self):
        return EventsQuerySet(self.model)


class PrismQuerySet(models.QuerySet):

    def visible(self):
        return self.filter(is_hidden=False)


class AnnouncementQuerySet(models.QuerySet):
    """QuerySet для анонсов"""

    def active(self, stamp=None):
        """Активные анонсы на момент времени stamp

        :type stamp: datetime.Date
        """

        stamp = stamp or datetime.date.today()
        return self.filter(start__lte=stamp, end__gte=stamp)

    def for_place(self, place):
        """Анонсы для конкретного места места

        :type place: идентификатор места из Announcement.PLACE_CHOICES
        """

        return self.filter(Q(place=place) | Q(place__isnull=True))


class TicketEventQuerySet(models.QuerySet):
    """QuerySet для событий из билетной системы"""

    def active(self, stamp=None):
        """
        Активные сеансы на момент времени stamp
        Если stamp не указан, берется текущий момент.
        """

        stamp = stamp or datetime.datetime.now()

        return self.filter(sessions__datetime__gte=stamp).distinct()


class CurrentSessionQuerySet(models.QuerySet):
    def with_tickets(self):
        return self.prefetch_related('kinomaxsession', 'ramblersession', 'kassysession')
