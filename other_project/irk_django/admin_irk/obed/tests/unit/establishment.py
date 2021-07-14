# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import sys
import mock
from freezegun import freeze_time

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G, N

from irk.afisha.models import Genre, Guide, EventGuide, Period, Sessions, Event, EventType
from irk.map.models import Cities as City
from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.phones.models import Sections as Section, MetaSection, Address, Worktime
from irk.tests.unit_base import UnitTestBase

from irk.obed.models import Establishment, Type, GuruCause, Menu, ArticleCategory


class EstablishmentTestCase(UnitTestBase):
    """Тесты заведений обеда"""

    csrf_checks = False

    def setUp(self):
        G(MetaSection, alias='food')
        super(EstablishmentTestCase, self).setUp()
        self.user = self.create_user('user')
        self.admin = self.create_user('admin', '123', is_admin=True)
        self.ct = ContentType.objects.get_for_model(Establishment)
        self.section_cafe = G(Section, slug='cafe', content_type=self.ct)
        self.section_delivery = G(Section, slug='delivery', content_type=self.ct)
        self.today = datetime.date.today()

    def create_establishment(self, visible=True, user=None, firms_ptr=None, section=None, last_review=None):
        if not section:
            section = self.section_cafe
        establishment = N(Establishment, main_section=section, name=self.random_string(10), visible=visible,
                          user=user, last_review=last_review)
        if firms_ptr:
            establishment.firms_ptr = firms_ptr

        establishment.save()
        establishment.section.add(section)
        establishment.types.add(G(Type))
        return establishment

    def test_read(self):
        """Страница заведения"""

        est = self.create_establishment(visible=True)
        self.create_establishment(visible=False)
        for _ in xrange(1, 9):
            self.create_establishment(visible=True, section=self.section_delivery)
        for _ in xrange(1, 11):
            self.create_establishment(visible=True, section=self.section_cafe)

        site = Site.objects.get(slugs='obed')
        category = G(ArticleCategory, title=u'Критик', slug='critic')

        article = create_material('obed', 'article', section_category=category, site=site,  is_hidden=False, mentions=[est, ])

        url = reverse('obed:establishment_read', kwargs={'section_slug': est.main_section.slug,
                                                               'firm_id': est.pk})
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/establishment/read.html')
        self.assertEqual(response.context['object'], est)

        self.assertIn(article, response.context['mentions'])

        est.visible = False
        est.save()

    def test_load_tab_menu(self):
        """Меню заведения"""
        est = self.create_establishment(visible=True)
        menu = G(Menu, establishment=est)

        url = reverse('obed:establishment:menu', kwargs={'firm_id': est.pk})
        response = self.app.get(url, xhr=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/establishment/read_ajax_menu.html')
        self.assertEqual(response.context['menu'], menu)

    def test_load_tab_comments(self):
        """Отзывы заведения"""
        est = self.create_establishment(visible=True)

        url = reverse('obed:establishment:comments', kwargs={'firm_id': est.pk})
        response = self.app.get(url, xhr=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/establishment/read_ajax_comments.html')
        self.assertEqual(est, response.context['obj'])

    def test_load_tab_events(self):
        """События заведения"""

        day = datetime.date.today() + datetime.timedelta(days=2)

        self.event_type = G(EventType, alias='night')
        genre = G(Genre)
        guide = G(Guide, event_type=self.event_type)
        est = self.create_establishment(visible=True, firms_ptr=guide.firms_ptr)

        event = G(Event, type=self.event_type, genre=genre, is_hidden=False,
                  is_obed_announcement=True, parent=None)
        event_guide = G(EventGuide, event=event, guide=guide)
        period = G(Period, event_guide=event_guide, duration=None, start_date=day,
                   end_date=day)
        G(Sessions, period=period, time=datetime.time(12, 0))
        G(Sessions, period=period, time=datetime.time(13, 0))

        url = reverse('obed:establishment:events', kwargs={'firm_id': est.pk})
        response = self.app.get(url, xhr=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/establishment/read_ajax_events.html')
        self.assertEqual(2, len(response.context['announcements']))


    @mock.patch('irk.irk.phones.views.base.mixins.FirmBaseViewMixin.get_form')
    def test_add_establishment(self, get_form):
        """Добавление заведения"""

        # Из-за того что форма является аттрибутом класса CreateFirmView, она инициализируется до того как в БД
        # загружаются рубрики и тест не проходит (ошибка валидации рубрик).
        # Подставляем правильно инициализированную форму
        sys.modules.pop('irk.obed.forms')
        from irk.obed.forms import EstablishmentForm
        get_form.return_value = EstablishmentForm

        response = self.app.get(reverse('obed:establishment:add'))
        self.assertEqual(response.status_code, 302)  # редирект для неавторизованных

        response = self.app.get(reverse('obed:establishment:add'), user=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/establishment/add.html')

        name = self.random_string(10)
        params = {
            'name': name,
            'section': self.section_cafe.id,
            'main_section': self.section_cafe.id,
            'contacts': self.random_string(5),
            'types': G(Type).id,
            'bill': Establishment.BILL_0_500,
            'address_set-0-city_id': City.objects.get(alias='irkutsk').id,
            'address_set-TOTAL_FORMS': 1,
            'address_set-INITIAL_FORMS': 0,
            'address_set-MAX_NUM_FORMS': 1,
            'gallerypicture_set-TOTAL_FORMS': 48,
            'gallerypicture_set-INITIAL_FORMS': 0,
            'gallerypicture_set-MAX_NUM_FORMS': 48,
        }

        response = self.app.post(reverse('obed:establishment:add'), params, user=self.user)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/establishment/added.html')
        self.assertEqual(Establishment.objects.filter(name=name).exists(), True)

    @mock.patch('irk.irk.phones.views.base.mixins.FirmBaseViewMixin.get_form')
    def test_edit_establishment(self, get_form):
        """Редактирование заведения"""

        # Из-за того что форма является аттрибутом класса UpdateFirmView, она инициализируется до того как в БД
        # загружаются рубрики и тест не проходит (ошибка валидации рубрик).
        # Подставляем правильно инициализированную форму
        sys.modules.pop('irk.obed.forms')
        from irk.obed.forms import EstablishmentForm
        get_form.return_value = EstablishmentForm

        est = self.create_establishment(user=self.user)

        response = self.app.get(reverse('obed:establishment:edit', args=(est.id, )))
        self.assertEqual(response.status_code, 302)  # левых юзеров лесом

        response = self.app.get(reverse('obed:establishment:edit', args=(est.id, )), user=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/establishment/edit.html')

        name = self.random_string(10)
        params = {
            'name': name,
            'section': self.section_cafe.id,
            'main_section': self.section_cafe.id,
            'contacts': self.random_string(5),
            'types': G(Type).id,
            'bill': Establishment.BILL_0_500,
            'address_set-0-city_id': City.objects.get(alias='irkutsk').id,
            'address_set-TOTAL_FORMS': 1,
            'address_set-INITIAL_FORMS': 0,
            'address_set-MAX_NUM_FORMS': 1,
            'gallerypicture_set-TOTAL_FORMS': 48,
            'gallerypicture_set-INITIAL_FORMS': 0,
            'gallerypicture_set-MAX_NUM_FORMS': 48,
        }
        old_name = est.name
        url = reverse('obed:establishment:edit', args=(est.id, ))
        response = self.app.post(url, params, user=self.user).follow()

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/establishment/edit.html')
        new_name = Establishment.objects.get(id=est.id).name
        self.assertEqual(new_name, name)
        self.assertNotEqual(new_name, old_name)

    def test_edit_establishment_for_authorized_user(self):
        """Авторизованный пользователь не относящийся к заведению не может его редактировать"""

        est = self.create_establishment(user=self.user)
        url = reverse('obed:establishment:edit', args=(est.id, ))

        hacker = self.create_user('hacker')

        response = self.app.get(url, user=hacker, expect_errors=True)
        self.assertEqual(response.status_code, 403)


class EstablishmentListTestCase(UnitTestBase):
    """Тесты для списка заведений"""

    def setUp(self):
        super(EstablishmentListTestCase, self).setUp()
        self.ct = ContentType.objects.get_for_model(Establishment)
        self.section = G(Section, slug='cafe', content_type=self.ct)
        self.url = reverse('obed:section_list', kwargs={'section_slug': self.section.slug})

    def test_method_get_no_filter_sorting_by_name(self):
        """
        Список заведений для конкретной рубрики на первой странице без фильтра, сортировка по имени.

        Ожидаемый ответ: 3 топовых заведения, 20 остальных заведений (сортировка по имени)
        """
        self._create_establishments(number=50)
        self._create_top_establishments(number=3)

        response = self.app.get(self.url)
        self.assertEqual(3, len(response.context['top_list']))
        self.assertEqual(20, len(response.context['object_list']))
        self.assertTrue(response.context['has_next'])
        self.assertEqual(20, response.context['next_start_index'])
        self.assertEqual(24, response.context['next_limit'])
        self.assertEqual(53, response.context['total_object_count'])
        self.assertEqual(self.section, response.context['current_section'])


    def test_method_get_with_filter_sorting_by_name(self):
        """
        Список заведений для конкретной рубрики на первой странице с фильтром, сортировка по имени.

        Ожидаемый ответ: список из 23 заведений с танцполом. Топовых заведений нет.
        """

        self._create_establishments()
        self._create_top_establishments()
        G(Establishment, visible=True, section=[self.section], last_review=None, n=30, dancing=True)

        response = self.app.get(self.url, params={'dancing': True})
        self.assertEqual(0, len(response.context['top_list']))
        self.assertEqual(23, len(response.context['object_list']))
        self.assertTrue(response.context['has_next'])
        self.assertEqual(23, response.context['next_start_index'])
        self.assertEqual(7, response.context['next_limit'])
        self.assertEqual(30, response.context['total_object_count'])
        self.assertEqual(self.section, response.context['current_section'])
        for est in response.context['object_list']:
            self.assertTrue(est.dancing)

    def test_method_ajax_no_filter_sorting_by_name(self):
        """
        Запрос через Ajax следующей части списка заведений  для конкретной рубрики без фильтра, сортировка по имени.
        """
        self._create_establishments(number=40)
        self._create_top_establishments(number=3)

        response = self.app.get(self.url, xhr=True, params={'start': 24})
        self.assertIn('html', response.json)
        self.assertFalse(response.json['has_next'])
        self.assertEqual(40, response.json['next_start_index'])
        self.assertEqual(0, response.json['next_limit'])

    def test_method_ajax_with_filter_sorting_by_name(self):
        """
        Запрос через Ajax следующей части списка заведений для конкретной рубрики с фильтром, сортировка по имени.
        """
        self._create_establishments(number=50)
        self._create_top_establishments(number=3)
        G(Establishment, visible=True, section=[self.section], last_review=None, n=30, dancing=True)

        response = self.app.get(self.url, xhr=True, params={'dancing': True, 'start': 24, 'limit': 10})

        self.assertIn('html', response.json)
        self.assertFalse(response.json['has_next'])
        self.assertEqual(30, response.json['next_start_index'])
        self.assertEqual(0, response.json['next_limit'])

    def test_standard_workflow(self):
        """
        Проверка стандартного рабочего процесса для списка заведений.

        Дано: 50 обычных заведения, 3 топовых.
        1. На GET запрос возвращается 3 топовых заведения, 20 обычных, 1 место занято под баннер.
            следующая страница: есть, стартовый индекс: 20, число объектов на ней: 24
        2. На 1й ajax запрос позвращается 24 обычных заведения.
            следующая страница: есть, стартовый индекс: 44, число объектов на ней: 6
        3. На 2й ajax запрос позвращается 6 обычных заведений.
            следующая страница: нет, стартовый индекс: 50, число объектов на ней: 0
        """
        self._create_establishments(number=50)
        self._create_top_establishments(number=3)

        response = self.app.get(self.url)
        self.assertEqual(3, len(response.context['top_list']))
        self.assertEqual(20, len(response.context['object_list']))
        self.assertEqual(53, response.context['total_object_count'])
        self.assertTrue(response.context['has_next'])
        self.assertEqual(20, response.context['next_start_index'])
        self.assertEqual(24, response.context['next_limit'])

        response = self.app.get(self.url, xhr=True, params={'start': response.context['next_start_index'],
                                                            'limit': response.context['next_limit']})
        self.assertTrue(response.json['has_next'])
        self.assertEqual(44, response.json['next_start_index'])
        self.assertEqual(6, response.json['next_limit'])

        response = self.app.get(self.url, xhr=True, params={'start': response.json['next_start_index'],
                                                            'limit': response.json['next_limit']})
        self.assertFalse(response.json['has_next'])
        self.assertEqual(50, response.json['next_start_index'])
        self.assertEqual(0, response.json['next_limit'])

    def test_ajax_boundary_conditions(self):
        """Проверка граничных условий при Ajax запросах"""
        self._create_establishments(number=50)
        self._create_top_establishments(number=3)

        # Минимальный значение для параметра start равно 0
        response = self.app.get(self.url, xhr=True, params={'start': -1, 'limit': 10})
        self.assertTrue(response.json['has_next'])
        self.assertEqual(10, response.json['next_start_index'])

        self.assertEqual(24, response.json['next_limit'])

        response = self.app.get(self.url, xhr=True, params={'start': 0, 'limit': 10})
        self.assertTrue(response.json['has_next'])
        self.assertEqual(10, response.json['next_start_index'])
        self.assertEqual(24, response.json['next_limit'])

        # Максимально можно запросить 24 элемента
        response = self.app.get(self.url, xhr=True, params={'start': 1, 'limit': 30})
        self.assertTrue(response.json['has_next'])
        self.assertEqual(25, response.json['next_start_index'])
        self.assertEqual(24, response.json['next_limit'])

        response = self.app.get(self.url, xhr=True, params={'start': 45, 'limit': 10})
        self.assertFalse(response.json['has_next'])
        self.assertEqual(50, response.json['next_start_index'])
        self.assertEqual(0, response.json['next_limit'])

        response = self.app.get(self.url, xhr=True, params={'start': 49, 'limit': 1})
        self.assertFalse(response.json['has_next'])
        self.assertEqual(50, response.json['next_start_index'])
        self.assertEqual(0, response.json['next_limit'])

        response = self.app.get(self.url, xhr=True, params={'start': 50, 'limit': 1})
        self.assertFalse(response.json['has_next'])
        self.assertEqual(50, response.json['next_start_index'])
        self.assertEqual(0, response.json['next_limit'])

        response = self.app.get(self.url, xhr=True, params={'start': 51, 'limit': 1})
        self.assertFalse(response.json['has_next'])
        self.assertEqual(50, response.json['next_start_index'])
        self.assertEqual(0, response.json['next_limit'])

    def test_list_filter_boll_establishment(self):
        """Фильтр списка заведений по галочкам"""

        establishment = G(Establishment, name=self.random_string(10), visible=True, last_review=None)
        response = self.app.get(reverse('obed:list'))
        self.assertEqual(response.context['object_list'][0], establishment)

        boolean_fields = ('wifi', 'dancing', 'karaoke', 'children_room', 'business_lunch')

        for boolean_field in boolean_fields:
            params = {boolean_field: True}
            establishment = G(Establishment, name=self.random_string(10), visible=True, **params)
            response = self.app.get(reverse('obed:list'), params=params)
            self.assertEqual(response.context['object_list'][0], establishment,
                             'Error filter for {}'.format(boolean_field))

    def test_list_filter_types_establishment(self):
        """Фильтр списка заведений по кухне"""

        types = G(Type)
        G(Type, n=3)
        establishment = G(Establishment, name=self.random_string(10), visible=True, types=[types, ], last_review=None)
        params = {'types': types.pk}
        response = self.app.get(reverse('obed:list'), params=params)
        self.assertEqual(response.context['object_list'][0], establishment)

    def test_list_filter_gurucause_establishment(self):
        """Фильтр списка заведений по гуру"""

        establishment = G(Establishment, name=self.random_string(10), visible=True, last_review=None)
        gurucause = G(GuruCause, establishments=[establishment, ])
        G(GuruCause, n=3)
        params = {'gurucause': gurucause.pk}
        response = self.app.get(reverse('obed:list'), params=params)
        self.assertEqual(response.context['object_list'][0], establishment)

    def test_list_filter_twenty_four_hour_establishment(self):
        """Фильтр работы заведения 24 часа"""

        city_irkutsk = City.objects.get(alias='irkutsk')

        est_empty = G(Establishment, name=self.random_string(10), visible=True)
        G(Address, twenty_four_hour=False, is_main=True, city_id=city_irkutsk, firm_id=est_empty)
        est_24 = G(Establishment, name=self.random_string(10), visible=True)
        G(Address, twenty_four_hour=True, is_main=True, city_id=city_irkutsk, firm_id=est_24)
        response = self.app.get(reverse('obed:list'))
        self.assertEqual(len(response.context['object_list']), 2)

        params = {'work_24_hour': True}
        response = self.app.get(reverse('obed:list'), params=params)
        self.assertEqual(response.context['object_list'][0], est_24)

    def test_list_filter_bill_establishment(self):
        """Фильтр списка заведений по стоимости счета"""

        G(Establishment, name=self.random_string(10), bill=Establishment.BILL_0_500, visible=True)
        G(Establishment, name=self.random_string(10), bill=Establishment.BILL_0_500, visible=True)
        G(Establishment, name=self.random_string(10), bill=Establishment.BILL_500_1000, visible=True)
        G(Establishment, name=self.random_string(10), bill=Establishment.BILL_500_1000, visible=True)
        G(Establishment, name=self.random_string(10), bill=Establishment.BILL_500_1000, visible=True)
        G(Establishment, name=self.random_string(10), bill=Establishment.BILL_1000_1500, visible=True)
        G(Establishment, name=self.random_string(10), bill=Establishment.BILL_1500_INF, visible=True)
        G(Establishment, name=self.random_string(10), bill=Establishment.BILL_1500_INF, visible=True)

        url = reverse('obed:list')

        response = self.app.get('{}?bill=1'.format(url))
        self.assertEqual(len(response.context['object_list']), 2)
        response = self.app.get('{}?bill=3'.format(url))
        self.assertEqual(len(response.context['object_list']), 4)
        response = self.app.get('{}?bill=4'.format(url))
        self.assertEqual(len(response.context['object_list']), 2)
        response = self.app.get('{}?bill=1&bill=4'.format(url))
        self.assertEqual(len(response.context['object_list']), 4)
        response = self.app.get('{}?bill=1&bill=3&bill=4'.format(url))
        self.assertEqual(len(response.context['object_list']), 8)

    def _create_establishments(self, number=50):
        """
        Создать необходимое количество заведений

        :param number: Количество создаваемых заведений
        """
        return G(Establishment, visible=True, section=[self.section], last_review=None, n=number)


class EstablishmentListTwoHourFilterTestCase(UnitTestBase):
    """Тесты фильтра работы заведений еще 2 часа"""

    def setUp(self):
        self.url = reverse('obed:list')
        self.params = {'open_2_hour': True}

        self._populate()

    def _populate(self):
        """Заполнить базу данных тестовыми данными"""

        # TODO: занимает довольно продолжительное время.
        # Пытался перенести в setUpClass, но после выполнения первого теста БД очищается.

        city = City.objects.get(alias='irkutsk')

        # Без времени работы
        self.est_empty = G(Establishment, name=u'est_empty', visible=True)
        G(Address, twenty_four_hour=False, is_main=True, city_id=city, firm_id=self.est_empty)

        # Круглосуточно
        self.est_24 = G(Establishment, name=u'est_24', visible=True)
        G(Address, twenty_four_hour=True, is_main=True, city_id=city, firm_id=self.est_24)

        # Ежедневно с 8:30 - 17:30
        self.est_every_day = G(Establishment, name=u'est_every_day', visible=True)
        address = G(Address, twenty_four_hour=False, is_main=True, city_id=city,
                    firm_id=self.est_every_day)
        for i in xrange(0, 7):
            G(Worktime, address=address, weekday=i, start_time=datetime.time(hour=8, minute=30),
              end_time=datetime.time(hour=17, minute=30))

        # Будни с 9:00 - 18:00
        self.est_work_day = G(Establishment, name=u'est_work_day', visible=True)
        address = G(Address, twenty_four_hour=False, is_main=True, city_id=city,
                    firm_id=self.est_work_day)
        for i in xrange(0, 5):
            G(Worktime, address=address, weekday=i, start_time=datetime.time(hour=9),
              end_time=datetime.time(hour=18))

        # пт-вс с 19:00 - 01:00
        self.est_fr_to_sun_day_late = G(Establishment, name=u'est_fr_to_sun_day_late', visible=True)
        address = G(Address, twenty_four_hour=False, is_main=True, city_id=city,
                    firm_id=self.est_fr_to_sun_day_late)
        for i in xrange(4, 7):
            G(Worktime, address=address, weekday=i, start_time=datetime.time(hour=19),
              end_time=datetime.time(hour=1))

        # Ежедневно с 10:00 - 03:00
        self.est_every_day_late = G(Establishment, name=u'est_every_day_late', visible=True)
        address = G(Address, twenty_four_hour=False, is_main=True, city_id=city,
                    firm_id=self.est_every_day_late)
        for i in xrange(0, 7):
            G(Worktime, address=address, weekday=i, start_time=datetime.time(hour=10),
              end_time=datetime.time(hour=3))

    def test_not_filter(self):
        """Запрос заведений без фильтра"""

        response = self.app.get(self.url)
        self.assertEqual(len(response.context['object_list']), 6)

    @freeze_time('2014-07-21 00:00')    # Пн 00:00
    def test_monday_midnight(self):
        """Понедельник полночь"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(response.context['object_list'], [self.est_24, self.est_every_day_late])

    @freeze_time('2014-07-21 02:00')    # Пн 02:00
    def test_monday_two_hours(self):
        """Понедельник два часа"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(response.context['object_list'], [self.est_24, ])

    @freeze_time('2014-07-21 07:00')    # Пн 07:00
    def test_monday_seven_hours(self):
        """Понедельник семь часов"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(response.context['object_list'], [self.est_24, ])

    @freeze_time('2014-07-21 09:00')    # Пн 09:00
    def test_monday_nine_hours(self):
        """Понедельник девять часов"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(response.context['object_list'], [self.est_24, self.est_every_day, self.est_work_day])

    @freeze_time('2014-07-21 12:00')    # Пн 12:00
    def test_monday_twelve_hours(self):
        """Понедельник двенадцать часов"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(
            response.context['object_list'],
            [self.est_24, self.est_every_day, self.est_work_day, self.est_every_day_late]
        )

    @freeze_time('2014-07-21 16:00')    # Пн 16:00
    def test_monday_sixteen_hours(self):
        """Понедельник шестнадцать часов"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(
            response.context['object_list'], [self.est_24, self.est_work_day, self.est_every_day_late]
        )

    @freeze_time('2014-07-21 18:00')    # Пн 18:00
    def test_monday_eighteen_hours(self):
        """Понедельник восемнадцать часов"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(response.context['object_list'], [self.est_24, self.est_every_day_late])

    @freeze_time('2014-07-22 01:00')    # Вт 1:00
    def test_tuesday_one_hours(self):
        """Вторник первый час"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(response.context['object_list'], [self.est_24, self.est_every_day_late])

    @freeze_time('2014-07-25 16:00')    # Пт 16:00
    def test_friday_sixteen_hours(self):
        """Пятница шестнадцать часов"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(
            response.context['object_list'], [self.est_24, self.est_work_day, self.est_every_day_late]
        )

    @freeze_time('2014-07-25 19:00')    # Пт 19:00
    def test_friday_nineteen_hours(self):
        """Пятница девятнадцать часов"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(
            response.context['object_list'], [self.est_24, self.est_fr_to_sun_day_late, self.est_every_day_late]
        )

    @freeze_time('2014-07-25 23:30')    # Пт 23:30
    def test_friday_twenty_three_hours_thirty_minutes(self):
        """Пятница двадцать три часа тридцать минут"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(response.context['object_list'], [self.est_24, self.est_every_day_late])

    @freeze_time('2014-07-27 22:00')    # Вс 22:00
    def test_sunday_twenty_two_hours(self):
        """Воскресенье двадцать два часа"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(
            response.context['object_list'], [self.est_24, self.est_fr_to_sun_day_late, self.est_every_day_late]
        )

    @freeze_time('2014-07-27 23:30')    # Вс 23:30
    def test_sunday_twenty_three_hours_thirty_minutes(self):
        """Воскресенье двадцать три часа тридцать минут"""

        response = self.app.get(self.url, params=self.params)
        self.assertItemsEqual(response.context['object_list'], [self.est_24, self.est_every_day_late])
