# -*- coding: utf-8 -*-

import datetime

from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase

from irk.afisha.models import Guide, EventType, Genre, Event, EventGuide, Period, Sessions
from irk.phones.models import Sections, Address
from irk.map.models import Cities
from irk.obed.models import Establishment


class GuideTestCase(UnitTestBase):
    """ Тестирование гида """

    def setUp(self):
        super(GuideTestCase, self).setUp()
        self.event_type = G(EventType, alias='night')

    def test_guide_read_session_sort(self):
        """ Сортировка времени события на странице гида """

        tomorrow = datetime.date.today() + datetime.timedelta(1)
        after_tomorrow = datetime.date.today() + datetime.timedelta(2)

        event_type = G(EventType, alias='cinema')
        genre = G(Genre)
        guide = G(Guide, event_type=event_type, visible=True)
        event = G(Event, type=event_type, genre=genre, parent=None, is_hidden=False)
        event_guide = G(EventGuide, event=event, guide=guide, hall=None)
        period = G(Period, event_guide=event_guide, start_date=tomorrow, end_date=after_tomorrow, duration=None)
        G(Sessions, period=period, time=datetime.time(18, 0))
        G(Sessions, period=period, time=datetime.time(0, 0))
        G(Sessions, period=period, time=datetime.time(13, 0))
        G(Sessions, period=period, time=datetime.time(1, 0))

        context = self.app.get(reverse('guide:read', kwargs={'firm_id': guide.pk})).context

        self.assertEqual(context['schedule'][0][1][0][1]['sessions'][0].time, datetime.time(13, 0))
        self.assertEqual(context['schedule'][0][1][0][1]['sessions'][1].time, datetime.time(18, 0))
        self.assertEqual(context['schedule'][0][1][0][1]['sessions'][2].time, datetime.time(0, 0))
        self.assertEqual(context['schedule'][0][1][0][1]['sessions'][3].time, datetime.time(1, 0))

    def test_new_guide(self):
        """ Вывод завдения в списке и на странице """

        section = G(Sections, is_guide=True, on_guide_index=True, content_type=None)
        city = Cities.objects.get(pk=1)
        guide = G(Guide, event_type=self.event_type)
        guide.visible = True
        guide.save()
        guide.section.add(section)
        G(Address, firm_id=guide.firms_ptr, city_id=city)

        page = self.app.get(reverse('guide:rubric'))
        self.assertEqual(1, len(page.context['firms_arr']))
        self.assertEqual(guide, page.context['firms_arr'][0][0])

    def test_obed_redirect(self):
        """ Редирект заведения в обед, если нет расписания """

        ct = ContentType.objects.get_for_model(Establishment)
        section = G(Sections, is_guide=True, slug=self.random_string(5), on_guide_index=True, content_type=ct)
        city = Cities.objects.get(pk=1)
        guide = G(Guide, event_type=self.event_type, visible=True)
        guide.section.add(section)
        G(Address, firm_id=guide.firms_ptr, city_id=city)
        G(Establishment, main_section=section, firms_ptr=guide.firms_ptr, visible=True, last_review=None)
        page = self.app.get(guide.get_absolute_url(), auto_follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertIn('/obed/', page.context['request'].path)

    def test_expected_schedule(self):
        """ Тестирование вывода расписания, если нет текущего """

        kwargs = {
            'fill_nullable_fields': False,
        }

        date = datetime.date.today() + datetime.timedelta(1)

        section = G(Sections, is_guide=True, on_guide_index=True, content_type=None)
        city = Cities.objects.get(pk=1)
        guide = G(Guide, event_type=self.event_type)
        guide.visible = True
        guide.save()
        guide.section.add(section)
        G(Address, firm_id=guide.firms_ptr, city_id=city)

        genre = G(Genre)
        event = G(Event, type=self.event_type, genre=genre, is_hidden=False, **kwargs)
        event_guide = G(EventGuide, event=event, guide=guide, **kwargs)

        period = G(Period, event_guide=event_guide, duration=None, start_date=date, end_date=date)

        G(Sessions, period=period, time=datetime.time(12, 0))
        page = self.app.get(guide.get_absolute_url())
        self.assertEqual(1, len(page.context['schedule']))
