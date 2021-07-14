# -*- coding: utf-8 -*-

import datetime
import operator
import re

from django.contrib.contenttypes.models import ContentType
from django.db import connection

from irk.afisha.models import Event, EventGuide, Genre, Guide, Hall, Period
from irk.afisha.models import Sessions as EventSession
from irk.phones.models import Address
from irk.phones.models import Sections as Section
from irk.utils.notifications import tpl_notify

ZERO_TIME = datetime.time(0, 0, 0)


class Day(object):
    def __init__(self, date, qs):
        self.date = date
        self.periods = qs

    def get_expected_session(self):
        now = datetime.datetime.now()
        if hasattr(self.periods[0], 'sessions'):
            for session in self.periods[0].sessions:
                if session.time >= now.time():
                    session.period = self.periods[0]
                    return session

        return True


def compare(key):
    """Функция для сортировки сеансов"""

    if not hasattr(key, 'sessions'):
        return ZERO_TIME
    try:
        return key.sessions[0].time
    except IndexError:
        pass
    return ZERO_TIME


class Sessions(object):
    """
        Класс Который представляет сеансы либо для гида , либо события.
        @param object: Guide|Event
        @param date: дата 
    """

    object = None
    date = None
    ct = None
    cursor = None

    _last_date_ = -1
    _first_date_ = -1

    _next_week_ = []
    _prev_week_ = []
    _week_ = []
    _periods_ = None
    _filter_ = {}

    def __init__(self, object, date, event_guide_filter=None):
        self.object, self.date = object, date
        self.ct = ContentType.objects.get_for_model(object)
        self._last_date_ = -1
        self._first_date_ = -1
        self._next_week_ = []
        self._prev_week_ = []
        self._week_ = []
        self._filter_ = event_guide_filter
        self.cursor = connection.cursor()

    def __getitem__(self, s):
        try:
            s = int(s)
        except:
            pass

        if type(s) is slice:
            return self.__iter__(s.start, s.stop)
        elif type(s) in [int, long]:
            iter = 0

            for x in self.__iter__():
                if iter == s:
                    return x
                iter += 1
        else:
            if s == 'last':
                return self.get_day(self.last_date)
            elif s == 'first':
                return self.get_day(self.first_date)
            elif s == "prev":
                return self.get_day(-1, None, -1)
            raise KeyError

    def next_week(self):
        """
            Следующая неделя
        """
        if not self._next_week_:
            next_week_first_day_index = 7 - self.date.weekday()
            next_week_index = None
            for day in self.__iter__(start=next_week_first_day_index):
                if day and not next_week_index or next_week_index == day.date.isocalendar()[1]:
                    next_week_index = day.date.isocalendar()[1]
                    self._next_week_.append(day)
                else:
                    break

        return self._next_week_

    def prev_week(self):
        """
            Предыдущая неделя
        """
        if not self._prev_week_:
            prev_week_first_day_index = -(self.date.weekday() + 1)
            prev_week_index = None
            for day in self.__iter__(start=prev_week_first_day_index, step=-1):
                if day and not prev_week_index or prev_week_index == day.date.isocalendar()[1]:
                    prev_week_index = day.date.isocalendar()[1]
                    self._prev_week_.append(day)
                else:
                    break
            self._prev_week_.reverse()
        return self._prev_week_

    def query(self, q):
        """
            Запрос к базе относительно текущего объекта.
        """
        field = "afisha_eventguide.%s_id=%s" % (self.ct.model, self.object.pk)
        self.cursor.execute(q % {'object': field})

    def next_date(self, date):
        """ Возвращает следующую дату по объекту 
            на которую есть события
        """

        if isinstance(self.object, Event):
            if 'city' in self._filter_:
                self.query("""
                        select afisha_period.start_date from afisha_period
                            left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                            left join afisha_guide on afisha_eventguide.guide_id = afisha_guide.firms_ptr_id
                            left join phones_address on phones_address.firm_id = afisha_guide.firms_ptr_id
                            where afisha_period.`end_date` >= '%s' and %%(object)s and phones_address.city_id = %s order by afisha_period.start_date ASC limit 1
                        """ % (date, self._filter_['city'].pk))
            else:
                self.query("""
                        select afisha_period.start_date from afisha_period
                            left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                            left join afisha_guide on afisha_eventguide.guide_id = afisha_guide.firms_ptr_id
                            left join phones_address on phones_address.firm_id = afisha_guide.firms_ptr_id
                            where afisha_period.`end_date` >= '%s' and %%(object)s order by afisha_period.start_date ASC limit 1
                        """ % (date))

        else:
            if 'hall' in self._filter_:
                self.query("""
                    select afisha_period.start_date
                    from afisha_period
                    left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                    left join `afisha_event` on afisha_event.id=afisha_eventguide.event_id
                    left join afisha_hall on afisha_hall.id=afisha_eventguide.hall_id
                    where  afisha_period.`end_date` >= '%s' and %%(object)s and afisha_hall.id=%d order by afisha_period.start_date ASC limit 1  
                """ % (date, self._filter_['hall'].id))
            else:
                self.query("""
                    select afisha_period.start_date
                    from afisha_period
                    left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                    left join `afisha_event` on afisha_event.id=afisha_eventguide.event_id
                    where  afisha_period.`end_date` >= '%s' and %%(object)s order by afisha_period.start_date ASC limit 1  
                """ % (date))

        rows = self.cursor.fetchall()
        if len(rows):
            closest_date = rows[0][0]
            return date if closest_date <= date else closest_date
        else:
            return date

    def __iter__(self, start=0, stop=None, step=1):
        day = start if start else 0
        iter = day

        now = datetime.date.today()

        if step > 0 and day < 0:
            # Если нам нужна предыдущая дата

            date = self['prev'].date + datetime.timedelta(day + 1)
        else:
            date = self.date + datetime.timedelta(day)

        if date < now and (self.next_date(date) - date) > datetime.timedelta(7):
            raise StopIteration

        while (step > 0 and self.last_date and date <= self.last_date and ( not stop or (iter < stop))) or (step < 0 and self.first_date and date >= self.first_date):
            if date < self.first_date:
                day += step

                if day < 0 and step > 0:
                    # Если с зади считаем то относительно первой предыдущей даты
                    date = self['prev'].date + datetime.timedelta(day)
                else:
                    date = self.date + datetime.timedelta(day)

                continue

            if isinstance(self.object, Event):
                if 'city' in self._filter_:
                    self.query("""
                        select distinct afisha_period.id,afisha_eventguide.id, afisha_period.price,afisha_sessions.time,afisha_sessions.order_time
                            ,afisha_guide.firms_ptr_id,phones_firms.name,afisha_hall.id,afisha_hall.name from afisha_period
                            left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                            left join afisha_guide on afisha_eventguide.guide_id = afisha_guide.firms_ptr_id
                            left join phones_address on phones_address.firm_id = afisha_guide.firms_ptr_id
                            left join phones_firms on phones_firms.id = afisha_guide.firms_ptr_id
                            left join afisha_sessions on afisha_sessions.period_id = afisha_period.id
                            left join afisha_hall on afisha_hall.id=afisha_eventguide.hall_id
                            where afisha_period.`start_date` <= '%s'  AND afisha_period.`end_date` >= '%s' and %%(object)s and phones_address.city_id = %s
                        """ % (date, date, self._filter_['city'].pk))
                else:
                    self.query("""
                        select distinct afisha_period.id,afisha_eventguide.id, afisha_period.price,afisha_sessions.time,afisha_sessions.order_time
                            ,afisha_guide.firms_ptr_id,phones_firms.name,afisha_hall.id,afisha_hall.name from afisha_period
                            left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                            left join afisha_guide on afisha_eventguide.guide_id = afisha_guide.firms_ptr_id
                            left join phones_address on phones_address.firm_id = afisha_guide.firms_ptr_id
                            left join phones_firms on afisha_guide.firms_ptr_id = phones_firms.id
                            left join afisha_sessions on afisha_sessions.period_id = afisha_period.id
                            left join afisha_hall on afisha_hall.id=afisha_eventguide.hall_id
                            where afisha_period.`start_date` <= '%s'  AND afisha_period.`end_date` >= '%s' and %%(object)s
                        """ % (date, date))

            else:
                if 'hall' in self._filter_:
                    self.query("""
                         select distinct afisha_period.id, afisha_eventguide.id, afisha_period.price,afisha_sessions.time,afisha_sessions.order_time
                            ,afisha_event.id,afisha_event.title,afisha_genre.name
                            from afisha_period
                            left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                            left join `afisha_event` on afisha_event.id=afisha_eventguide.event_id
                            left join afisha_genre on afisha_event.genreID=afisha_genre.id
                            left join afisha_sessions on afisha_sessions.period_id = afisha_period.id
                            left join afisha_hall on afisha_hall.id=afisha_eventguide.hall_id
                            where afisha_period.`start_date` <= '%s'  AND afisha_period.`end_date` >= '%s' and %%(object)s and afisha_hall.id=%d 
                        """ % (date, date, self._filter_['hall'].id))
                else:

                    self.query("""
                         select distinct afisha_period.id, afisha_eventguide.id, afisha_period.price,afisha_sessions.time,afisha_sessions.order_time
                            ,afisha_event.id,afisha_event.title,afisha_genre.name, afisha_hall.id as hall_id, afisha_hall.name as hall
                            from afisha_period
                            left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                            left join `afisha_event` on afisha_event.id=afisha_eventguide.event_id
                            left join afisha_genre on afisha_event.genreID=afisha_genre.id
                            left join afisha_sessions on afisha_sessions.period_id = afisha_period.id
                            left join afisha_hall on afisha_hall.id=afisha_eventguide.hall_id
                             where afisha_period.`start_date` <= '%s'  AND afisha_period.`end_date` >= '%s' and %%(object)s
                        """ % (date, date))

            rows = self.cursor.fetchall()

            if 'city' in self._filter_ and self._filter_['city'].pk == 1:
                self.query("""
                    select distinct afisha_period.id,afisha_eventguide.id, afisha_period.price,afisha_sessions.time,afisha_sessions.order_time
                                    ,Null,afisha_eventguide.guide_name,Null,Null from afisha_period
                                    left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                                    left join afisha_sessions on afisha_sessions.period_id = afisha_period.id
                                    where afisha_period.`start_date` <= '%s'  AND afisha_period.`end_date` >= '%s' and %%(object)s and afisha_eventguide.guide_id is NULL
                    """ % (date, date))
                rows += self.cursor.fetchall()

            period_set = {}
            map(period_set.__setitem__, [row[0] for row in rows], [])
            qs = []
            for period_pk in period_set.keys():
                period_data = filter(lambda x: x[0] == period_pk, rows)
                if isinstance(self.object, Event):
                    if period_data[0][5]:
                        if period_data[0][7]:
                            guide = Guide(id=period_data[0][5], name=period_data[0][6])
                            eg = EventGuide(guide=guide, hall=Hall(id=period_data[0][7], name=period_data[0][8], guide=guide))
                        else:
                            eg = EventGuide(guide=Guide(id=period_data[0][5], name=period_data[0][6]), )
                    else:
                        eg = EventGuide(pk=period_data[0][4], guide_name=period_data[0][6], guide=None)

                else:
                    if period_data[0][7]:
                        eg = EventGuide(event=Event(id=period_data[0][5], title=period_data[0][6], genre=Genre(name=period_data[0][7])), )
                    else:
                        eg = EventGuide(event=Event(id=period_data[0][5], title=period_data[0][6]), )

                    if len(period_data[0]) == 10:
                        hall = Hall(id=period_data[0][8], name=period_data[0][9])
                        eg.hall = hall

                period = Period(id=period_data[0][0], price=period_data[0][2], event_guide=eg)
                sessions = filter(lambda x: x[0], sorted([(row[4], row[3]) for row in period_data], key=operator.itemgetter(0)))
                if sessions:
                    sessions = map(lambda x: EventSession(time=x[1]), sessions)
                    setattr(period, 'sessions', sessions)
                qs.append(period)

            # Сортируем периоды так, чтобы сверху были те, которые начинаются раньше
            qs = sorted(qs, key=compare)

            data = Day(date, qs)
            day += step
            date = self.date + datetime.timedelta(day)
            if not qs:
                continue
            iter += step
            yield data

    def week(self):
        """
            Получает результат от текущей даты и до конца текущей недели.
        """
        if not self._week_:
            week_number = self.date.isocalendar()[1]
            for day in self:
                if day.date.isocalendar()[1] != week_number:
                    break
                self._week_.append(day)
        return self._week_

    def get_day(self, date=0, stop=None, step=1):
        """
            Получает объект дня
        """
        for x in self.__iter__(date, stop, step):
            return x

        return None

    def get_last_date(self):
        """
            Возвращает первую дату начальной привязки
        """
        if self._last_date_ == -1:
            try:
                self.query("""
                select afisha_period.end_date from afisha_period
                       left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                       where %(object)s  order by end_date DESC limit 1                
                """)

                self._last_date_ = self.cursor.fetchone()[0]
            except IndexError:
                self._last_date_ = None
            except TypeError:
                self._last_date_ = None

        return self._last_date_

    last_date = property(get_last_date)

    def get_first_date(self):
        """
            Возвращает конечную дату последней привязки
        """
        if self._first_date_ == -1:
            try:
                self.query("""
                    select afisha_period.start_date from afisha_period
                           left JOIN `afisha_eventguide` ON `afisha_period`.`event_guide_id` = `afisha_eventguide`.`id`
                           where %(object)s  order by start_date ASC limit 1                
                    """)
                self._first_date_ = self.cursor.fetchone()[0]
            except IndexError:
                self._first_date_ = None
            except TypeError:
                self._first_date_ = None
        return self._first_date_

    first_date = property(get_first_date)

    def get_nearest_date(self):
        """
            Получаем ближайшую к текущей дату сеансов.
        """
        now = datetime.datetime.now().date()
        if self.first_date and self.first_date >= now:
            return self.first_date
        elif self.last_date and self.last_date <= now:
            return self.last_date
        else:
            return now


def get_index_sections_with_guide(city):
    """Рубрики для индекса гида для определенного города

    Параметры::
        city: объект модели `map.models.Cities'
    """

    # TODO: кэш и инвалидация по сохранению `phones.models.Sections'
    sections = list(Section.objects.filter(on_guide_index=True).order_by('position'))
    maps = list(Guide._meta.get_field_by_name('section')[0].rel.through.objects.filter(sections__in=sections))
    guides = list(Guide.objects.filter(pk__in=[x.firms_id for x in maps], visible=True).select_related('firms_ptr'))
    addresses = list(Address.objects.filter(city_id=city, firm_id__in=guides).prefetch_related('streetid'))

    # Пост-кэширование
    for address in addresses:
        address.city_id = city

    result = []

    for section in sections:
        firms = []
        section_maps = [x.firms_id for x in maps if x.sections_id == section.pk]
        section_guides = [x for x in guides if x.pk in section_maps]
        for guide in section_guides:
            guide_addresses = sorted([x for x in addresses if x.firm_id_id == guide.pk], key=lambda x: x.is_main)[:1]
            if not guide_addresses:
                continue
            firms.append((guide, guide_addresses))
        columns = len(firms) / 2
        if len(firms) % 2 > 0:
            columns += 1

        firms = sorted(firms, key=lambda x: x[0].name)

        result.append((columns, firms, section))

    return result


AFISHA_EVENTS_FOR_DATE_QUERY = '''SELECT DISTINCT `afisha_event`.`id`, `afisha_event`.`title` AS afisha_title,
    `afisha_genre`.`name`, `afisha_event`.`comments_cnt`, `afisha_event`.`duration`, `afisha_event`.`production`,
    `afisha_event`.`info` FROM `afisha_period`
    LEFT JOIN `afisha_eventguide` ON `afisha_eventguide`.`id` = `afisha_period`.`event_guide_id`
    LEFT JOIN `afisha_event` ON `afisha_eventguide`.`event_id` = `afisha_event`.`id`
    LEFT JOIN `afisha_guide` ON `afisha_eventguide`.`guide_id` = `afisha_guide`.`firms_ptr_id`
    LEFT JOIN `phones_address` ON `phones_address`.`firm_id` = `afisha_guide`.`firms_ptr_id`
    LEFT JOIN `phones_firms` ON `phones_firms`.`id` = `afisha_guide`.`firms_ptr_id`
    LEFT JOIN `afisha_genre` ON `afisha_event`.`genreID` = `afisha_genre`.`id`
    WHERE
        `afisha_period`.`start_date` <= '%(date)s'
        AND `afisha_period`.`end_date` >= '%(date)s'
        AND `afisha_event`.`type_id` = %(type)s
        AND `phones_address`.`city_id` = %(city)s
'''


def events_for_date(date, city=1):
    cursor = connection.cursor()
    cursor.execute(AFISHA_EVENTS_FOR_DATE_QUERY % {'date': date.date(), 'city': city, 'type': 2})
    rows = cursor.fetchall()

    events = []
    for row in rows:
        events.append(Event(id=row[0], title=row[1], comments_cnt=row[3], duration=row[4], production=row[5], info=row[6], genre=Genre(name=row[2])))

    return events


def get_site_events(date, site, guide=None):
    """ Получаем события для сайта """

    now = datetime.datetime.now()

    curr = connection.cursor()

    if type(date) is datetime.date:
        date = [date, date]

    if date[0] == now.date():

        if guide:
            curr.execute("""
                        SELECT DISTINCT afisha_event.id,afisha_event.title,afisha_event.production,afisha_event.duration FROM `afisha_period`
                        INNER JOIN `afisha_eventguide` ON afisha_eventguide.id = afisha_period.event_guide_id
                        INNER JOIN afisha_event on afisha_event.id = afisha_eventguide.event_id
                        INNER Join afisha_guide on afisha_guide.firms_ptr_id = afisha_eventguide.guide_id
                        INNER JOIN afisha_sites_events on afisha_sites_events.event_id=afisha_event.id
                        INNER JOIN afisha_sessions on afisha_sessions.period_id = afisha_period.id
                        WHERE (afisha_period.`start_date` <= '%s' AND afisha_period.`end_date` >= '%s'  and afisha_sessions.time>'%s') and afisha_sites_events.site_id=%s and afisha_guide.firms_ptr_id=%s
            """ % (date[0], date[1], now.time(), site.pk, guide.pk))
        else:
            curr.execute("""
                        SELECT DISTINCT afisha_event.id,afisha_event.title,afisha_event.production,afisha_event.duration FROM `afisha_period`
                        INNER JOIN `afisha_eventguide` ON afisha_eventguide.id = afisha_period.event_guide_id
                        INNER JOIN afisha_event on afisha_event.id = afisha_eventguide.event_id
                        INNER Join afisha_guide on afisha_guide.firms_ptr_id = afisha_eventguide.guide_id
                        INNER JOIN afisha_sites_events on afisha_sites_events.event_id=afisha_event.id
                        INNER JOIN afisha_sessions on afisha_sessions.period_id = afisha_period.id
                        WHERE (afisha_period.`start_date` <= '%s' AND afisha_period.`end_date` >= '%s'  and afisha_sessions.time>'%s') and  afisha_sites_events.site_id=%s 
            """ % (date[0], date[1], now.time(), site.pk))
    else:

        if guide:
            curr.execute("""
                        SELECT DISTINCT afisha_event.id,afisha_event.title,afisha_event.production,afisha_event.duration FROM `afisha_period`
                        INNER JOIN `afisha_eventguide` ON afisha_eventguide.id = afisha_period.event_guide_id
                        INNER JOIN afisha_event on afisha_event.id = afisha_eventguide.event_id
                        INNER Join afisha_guide on afisha_guide.firms_ptr_id = afisha_eventguide.guide_id
                        INNER JOIN afisha_sites_events on afisha_sites_events.event_id=afisha_event.id
                        WHERE (afisha_period.`start_date` <= '%s' AND afisha_period.`end_date` >= '%s') and  afisha_sites_events.site_id=%s and afisha_guide.firms_ptr_id=%s
            """ % (date[0], date[1], site.pk, guide.pk))
        else:
            curr.execute("""
                        SELECT DISTINCT afisha_event.id,afisha_event.title,afisha_event.production,afisha_event.duration FROM `afisha_period`
                        INNER JOIN `afisha_eventguide` ON afisha_eventguide.id = afisha_period.event_guide_id
                        INNER JOIN afisha_event on afisha_event.id = afisha_eventguide.event_id
                        INNER Join afisha_guide on afisha_guide.firms_ptr_id = afisha_eventguide.guide_id
                        INNER JOIN afisha_sites_events on afisha_sites_events.event_id=afisha_event.id
                        WHERE (afisha_period.`start_date` <= '%s' AND afisha_period.`end_date` >= '%s') and  afisha_sites_events.site_id=%s 
            """ % (date[0], date[1], site.pk))

    result_events = []
    events = map(lambda row: dict(zip(map(lambda x: x[0], curr.description), row)), curr.fetchall())

    for event in events:
        event = Event(**event)
        event.get_sessions(date[0])
        result_events.append(event)

    return result_events


def time_to_ordertime(time):
    hour = (time.hour + 24) if time.hour in range(0, 7) else time.hour
    time = hour * 100 + time.minute
    return time


def update_cache_table(sender, **kwargs):
    print sender, kwargs


def get_price_for_period(period):
    """Получить цену для периода"""
    if period.price:
        return period.price
    event_guide = period.event_guide
    if event_guide:
        if event_guide.hall and event_guide.hall.price:
            return event_guide.hall.price
        elif event_guide.guide and event_guide.guide.price:
            return event_guide.guide.price
    return None


def get_price_for_session(session):
    """Получить цену для сеанса"""
    if session.price:
        return session.price
    period = session.period
    if period:
        return get_price_for_period(period)
    return None


def get_min_price(price):
    """Получить минимальное значение цены из строки"""
    min_price = None
    if price:
        m = re.search(r'(\d+)', price)
        if m:
            min_price = int(m.group())
    return min_price


def sent_event_open_notif(event):
    """Уведомление о размещении события пользователю"""
    if event.organizer_email:
        tpl_notify(u'Ваше событие размещено в афише Irk.ru', 'afisha/notif/event_opened.html', {'event': event},
                   emails=[event.organizer_email, ])
