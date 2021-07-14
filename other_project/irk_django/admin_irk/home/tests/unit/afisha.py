# -*- coding: utf-8 -*-

import datetime

from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase
from irk.afisha.models import Event, EventType, Genre, Guide, EventGuide, Period, Announcement
from irk.home.views import HomeView


class AfishaTestCase(UnitTestBase):
    def setUp(self):
        today = datetime.date.today()
        self.url = reverse('home_index')

        event_type = G(EventType, alias='cinema')
        genre = G(Genre)
        guide = G(Guide, event_type=event_type)
        start = datetime.date.today()
        end = start + datetime.timedelta(days=7)
        for _ in range(0, 5):
            event = G(Event, type=event_type, genre=genre, parent=None, is_hidden=False)
            G(Announcement, event=event, place=Announcement.PLACE_HOME_SLIDER, start=start, end=end)
            event_guide = G(EventGuide, event=event, guide=guide, hall=None)
            G(Period, event_guide=event_guide, start_date=today, end_date=today, n=5)

    def test(self):
        context = self.app.get(self.url).context
        an = context['afisha']['events']

        self.assertEqual(5, len(an))

    def test_rotation(self):
        """Проверяем ротацию

        В этом тесте мы расчитываем на то, что у нас в базе 5 событий, см. 22 строку этого файла
        """

        # Например, [1, 2, 3, 4, 5]
        events_ids = list(Event.objects.all().order_by('id').values_list('id', flat=True))

        for _ in range(10):
            context = self.app.get(self.url).context
            # В сессии уже хранится новое значение
            position_id = self.app.session[HomeView.AFISHA_ROTATION_SESSION_KEY] - 1
            if position_id < 0:
                position_id = len(events_ids) - 1

            check_list = events_ids[position_id:position_id + len(events_ids)]
            if position_id + len(events_ids) > len(events_ids):
                check_list += events_ids[:len(events_ids) - len(check_list)]

            ids = [x.id for x in context['afisha']['events']]

            self.assertEqual(check_list, ids)
