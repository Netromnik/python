# -*- coding: utf-8 -*-

import datetime
import random

from django_dynamic_fixture import G

from irk.afisha import models


def create_event(announce=True, **kwargs):
    """Создать событие"""

    date = kwargs.pop('date', datetime.date.today())
    time = kwargs.pop('time', datetime.time(12, 0))
    guide = kwargs.pop('guide', None) or G(models.Guide)

    event = G(models.Event, **kwargs)

    event_guide = G(models.EventGuide, event=event, guide=guide, fill_nullable_fields=False)
    period = G(
        models.Period, event_guide=event_guide, duration=None, start_date=date,
        end_date=date + datetime.timedelta(days=5), fill_nullable_fields=False
    )
    G(models.Sessions, period=period, time=time, fill_nullable_fields=False)

    if announce:
        G(models.Announcement, event=event, place=None, start=date, end=date + datetime.timedelta(days=5))

    return event


def create_material(**kwargs):
    """Создать материал"""

    material_class = random.choice([models.Article, models.Review, models.Photo])

    material = G(material_class, **kwargs)

    return material
