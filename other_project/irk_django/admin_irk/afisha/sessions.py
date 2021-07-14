# -*- coding: utf-8 -*-

import datetime
import logging

from irk.utils.helpers import time_combine


logger = logging.getLogger(__name__)


def update_schedule_specified(sender, **kwargs):
    """ При создании нового периода сначала создаем для него
        записи с расписанием `уточняется` """
    from irk.afisha.helpers import get_min_price, get_price_for_period

    created = kwargs.get('created')
    period = kwargs.get('instance')
    if not created:
        return

    min_price = get_min_price(get_price_for_period(period))
    now = datetime.datetime.now()
    from irk.afisha.models import CurrentSession
    today = datetime.date.today()
    current_date = period.start_date if period.start_date >= today else today
    while current_date <= period.end_date:
        real_date = datetime.datetime.combine(current_date, datetime.time(23, 59, 59))
        if real_date >= now:
            CurrentSession.objects.create(
                date=current_date,
                time=None,
                filter_time=None,
                fake_date=datetime.datetime.combine(current_date, datetime.time(0, 0, 0)),
                real_date=real_date,
                end_date=time_combine(real_date, period.duration),
                event_type=period.event_guide.event.type,
                event_guide=period.event_guide,
                guide=period.event_guide.guide,
                event=period.event_guide.event,
                is_hidden=period.event_guide.event.is_hidden,
                period=period,
                hall=period.event_guide.hall,
                is_3d=period.is_3d,
                min_price=min_price,
            )
        current_date += datetime.timedelta(1)


def update_cache_table(sender, **kwargs):
    """ При сохранении Event, EventGuide, Period, Sessions
        обновлет таблицу CurrentSessions
    """

    created = kwargs.get('created')
    instance = kwargs.get('instance')

    if created and not hasattr(instance, 'currentsession_set'):
        # для все объектов кроме сеансов
        # при изменении обекта меняем связанные записи
        # current_session
        return

    from irk.afisha.models import Period, EventGuide, Event
    current_sessions_qs = instance.currentsession_set.all()

    # Список полей, изменяемых в таблице модели `afisha.models.CurrentSessions'
    fields = {}

    event = None
    if isinstance(instance, Period):
        fields['is_3d'] = instance.is_3d
        event = instance.event_guide.event
    elif isinstance(instance, EventGuide):
        fields['hall'] = instance.hall_id
        fields['guide'] = instance.guide_id
        event = instance.event
    elif isinstance(instance, Event):
        fields['is_hidden'] = instance.is_hidden
        fields['event_type'] = instance.type_id
        event = instance

    if fields:
        logger.debug('Updating cache table with fields %(fields)s for instance %(model)s #%(id)d' % {
            'fields': fields,
            'module': instance._meta.object_name.lower(),
            'model': instance._meta.object_name,
            'id': instance.pk,
        })
        current_sessions_qs.update(**fields)

    if isinstance(instance, Period):
        # Если изменились даты то добавляем новые записи сеансов
        dates = current_sessions_qs.values_list("date", flat=True).distinct().order_by('date')
        if dates and instance.start_date == min(dates) and instance.end_date == max(dates):
            # Обновляем время у сеансов
            for session in current_sessions_qs:
                if session.time is not None:
                    session.filter_time = session.time
                    session.real_date = datetime.datetime.combine(session.date, session.filter_time)
                    session.fake_date = datetime.datetime.combine(session.date, session.time)

                    if session.time <= datetime.time(6, 0):
                        session.real_date += datetime.timedelta(1)

                    if instance.duration:
                        session.end_date = time_combine(session.real_date, instance.duration)
                    session.save()
        else:
            current_sessions_qs.delete()
            # Значит изменились даты
            # сохраняем привязанные сеансы
            for session in instance.sessions_set.all():
                session.save()

    # В ряде случаев задача на пересохранение события в афишу заканчивает работать раньше,
    # чем заканчивает работать эта функция, соответственно,
    # в поиск попадают неправильные данные из `afisha.models.CurrentSession`.
    # Вручную вызываем пересохранение события в поиск
    Event.search.model_search.update_search(event)


def add_cache_rows(sender, **kwargs):
    """ При создании записей Session
        1. Создаем записи в таблице CurrentSession
        2. Удаляем все записи с time=None и period=instance.period (т.е. те которые уточняются)
    """
    from irk.afisha.models import CurrentSession
    from irk.afisha.helpers import get_min_price, get_price_for_session

    # created = kwargs.get('created')
    instance = kwargs.get('instance')
    now = datetime.datetime.now()

    period = instance.period

    # Т.к. создается нормальный сеанс, то удаляем все записи `уточняется`
    period.currentsession_set.filter(time=None).delete()
    sessions = list(period.currentsession_set.exclude(time=None))

    min_price = get_min_price(get_price_for_session(instance))

    current_date = period.start_date
    while current_date <= period.end_date:
        # Если сеансы периода с такими датой и временем есть
        # то пропускаем дату
        if not len([s for s in sessions if s.date == current_date and s.time == instance.time
                    and s.min_price == min_price]):
            filter_time = instance.time
            real_date = datetime.datetime.combine(current_date, filter_time)
            if period.duration:
                real_date += datetime.timedelta(hours=period.duration.hour, minutes=period.duration.minute)
                filter_time = real_date.time()

            if instance.time <= datetime.time(6, 0):
                real_date += datetime.timedelta(1)

            if real_date >= now:
                CurrentSession.objects.create(
                    date=current_date,
                    time=instance.time,
                    filter_time=filter_time,
                    fake_date=datetime.datetime.combine(current_date, instance.time),
                    real_date=real_date,
                    end_date=time_combine(real_date, period.duration),
                    event_type=period.event_guide.event.type,
                    event_guide=period.event_guide,
                    guide=period.event_guide.guide,
                    event=period.event_guide.event,
                    is_hidden=period.event_guide.event.is_hidden,
                    period=period,
                    hall=period.event_guide.hall,
                    is_3d=period.is_3d,
                    min_price=min_price
                )
        current_date += datetime.timedelta(1)


def delete_cache_rows(sender, **kwargs):
    """ При удалении записей Session, удаляем CurrentSession объекты """
    from irk.afisha.models import CurrentSession
    from irk.afisha.helpers import get_min_price

    instance = kwargs.get('instance')
    CurrentSession.objects.filter(
        period_id=instance.period_id,
        time=instance.time,
        min_price=get_min_price(instance.price),
    ).delete()
