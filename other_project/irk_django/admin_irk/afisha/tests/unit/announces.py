# -*- coding: UTF-8 -*-

import datetime

from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from irk.afisha.controllers import ExtraAnnouncementsController, SliderAnnouncementsController
from irk.afisha.models import EventType, Genre, Guide, EventGuide, Period, Sessions, Announcement
from irk.afisha.templatetags.afisha_tags import afisha_extra_announcements
from irk.afisha.tests.utils import create_event, create_material
from irk.tests.unit_base import UnitTestBase


class AnnouncesTest(UnitTestBase):
    """ Тесты страниц анонсов"""

    def test_list(self):
        """ Тест списка анонсов"""

        date = datetime.date.today() + datetime.timedelta(1)
        event_type = G(EventType, alias='night')
        genre = G(Genre)
        guide = G(Guide, event_type=event_type)

        events = []

        kwargs = {
            'fill_nullable_fields': False,
            'guide': guide,
        }

        # Три события анонсируем
        event_with_anounce = [create_event(type=event_type, genre=genre, is_hidden=False, **kwargs) for i in range(3)]
        events.extend(event_with_anounce)
        # Одно не анонсируем
        event = create_event(announce=False, type=event_type, genre=genre, is_hidden=False, **kwargs)
        events.append(event)

        # событие, относящееся к другому типу
        event = create_event(type=G(EventType, alias='culture'), genre=genre, is_hidden=False, **kwargs)
        events.append(event)

        for event in events:
            event_guide = G(EventGuide, event=event, **kwargs)
            period = G(Period, event_guide=event_guide, duration=None, start_date=date, end_date=date)
            G(Sessions, period=period, time=datetime.time(12, 0))

        #  Список анонсов
        response = self.app.get(reverse('afisha:announces:events_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events']), 4)

        #  Список анонсов по типу события
        response = self.app.get(reverse('afisha:announces:events_list', kwargs={'event_type': event_type.alias}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events']), 3)


class ExtraAnnouncementsControllerTest(UnitTestBase):
    """Тесты контроллера дополнительных событий с анонсами"""

    def setUp(self):
        self._event_type = G(EventType, alias='night')
        date = datetime.date.today()

        kwargs = {'type': self._event_type, 'is_hidden': False}
        self._events_with_announce = [create_event(announce=False, **kwargs) for i in range(10)]
        for event in self._events_with_announce:
            G(
                Announcement, event=event, place=Announcement.PLACE_AFISHA_TYPE_PAGE, start=date,
                end=date + datetime.timedelta(days=5)
            )
        self._events_without_announce = [create_event(announce=False, **kwargs) for i in range(10)]

    def test_controller(self):
        """
        Проверка работы по умолчанию.

        Получить 6 первых событий с анонсами.
        """

        ctrl = ExtraAnnouncementsController(self._event_type)

        object_list, page_info = ctrl.get_announce_events(0, 6)

        self.assertEqual(6, len(object_list))
        self.assertListContains(self._events_with_announce, object_list)
        self.assertListNotContains(self._events_without_announce, object_list)
        self.assertTrue(page_info['has_next'])
        self.assertEqual(6, page_info['next_start_index'])
        self.assertEqual(4, page_info['next_limit'])

    def test_ajax_without_event_type(self):
        """Проверка ajax подгрузки"""

        url = u'{}?start=6&limit=10'.format(reverse('afisha_extra_announcements'))

        response = self.app.get(url)

        self.assertStatusIsOk(response)
        self.assertTrue(response.json['html'])
        self.assertFalse(response.json['has_next'])

    def test_template_tag(self):
        """Проверка шаблонного тега"""

        result = afisha_extra_announcements({})
        self.assertListContains(self._events_with_announce, result['announcement_list'])
        self.assertEqual(reverse('afisha_extra_announcements'), result['url'])

    def test_template_tag_with_event_type(self):
        """Проверка шаблонного тега для типа событий"""

        event_type = G(EventType, alias='night')

        result = afisha_extra_announcements({}, event_type=event_type)
        self.assertListContains(self._events_with_announce, result['announcement_list'])
        self.assertEqual(
            reverse('afisha:announces:extra', kwargs={'event_type_alias': self._event_type.alias}),
            result['url']
        )


class SliderAnnouncementsControllerTest(UnitTestBase):
    """Тесты контроллера анонсов в слайдере афиши"""

    def test_default(self):
        """
        Проверка стандартного поведения

        Возвращается максимум 10 объектов с анонсами как событий, так и материалов.
        """

        # 4 анонсируемых события
        kwargs = {'main_announcement': True, 'is_hidden': False}
        events = [create_event(**kwargs) for i in range(4)]

        # 3 анонсируемых материала
        kwargs = {'is_announce': True, 'is_hidden': False}
        materials = [create_material(**kwargs) for i in range(3)]

        ctrl = SliderAnnouncementsController()
        result = ctrl.get_announcements()

        self.assertEqual(7, len(result))
        self.assertListContains(result, materials)
        self.assertListContains(result, events)

        # Проверка, что у объектов есть отметка о их типе
        for obj in result:
            self.assertTrue(obj.announce_type in ['material', 'event'])

    def test_hidden(self):
        """Проверка отображения скрытых объектов"""

        hidden_event = create_event(is_hidden=True)
        hidden_material = create_material(is_announce=True, is_hidden=True)

        ctrl = SliderAnnouncementsController()
        result = ctrl.get_announcements()

        self.assertNotIn(hidden_event, result)
        self.assertNotIn(hidden_material, result)

        ctrl = SliderAnnouncementsController(show_hidden=True)
        result = ctrl.get_announcements()

        self.assertIn(hidden_event, result)
        self.assertIn(hidden_material, result)

    def test_by_event_type(self):
        """Анонсы по типу события содержат только события данного типа"""

        event_type = G(EventType, alias='night')
        # 4 анонсируемых события
        kwargs = {'type': event_type, 'is_hidden': False}
        events = [create_event(**kwargs) for i in range(4)]

        # 3 анонсируемых материала
        kwargs = {'is_announce': True, 'is_hidden': False}
        materials = [create_material(**kwargs) for i in range(3)]

        ctrl = SliderAnnouncementsController(event_type=event_type)
        result = ctrl.get_announcements()

        self.assertEqual(4, len(result))
        self.assertListContains(result, events)
        self.assertListNotContains(result, materials)
