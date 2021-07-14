# -*- coding: utf-8 -*-

from __future__ import absolute_import

from datetime import date

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from irk.tourism.models import TourFirm, Tour, TourDate, Place

from irk.phones.models import MetaSection, Sections as Section
from irk.tests.unit_base import UnitTestBase


class TourTest(UnitTestBase):
    """Тестирование туров"""

    csrf_checks = False

    def setUp(self):
        super(TourTest, self).setUp()

        G(MetaSection, id=2)

        self.anonymous = self.create_anonymous_user()
        self.hacker = self.create_user('hacker')
        self.owner = self.create_user('owner')
        self.admin = self.create_user('admin', is_admin=True)
        self.ct = ContentType.objects.get_for_model(TourFirm)
        self.section = G(Section,  content_type=self.ct, slug='tourfirm')

    def test_add_tour(self):
        """Добавление тура"""

        firm = G(TourFirm, visible=True, section=[self.section, ], user=self.owner)
        place = G(Place)

        url = reverse('tourism:firm:add_tour', args=(self.section.slug, firm.pk))

        # Анонимам доступ запрещен
        response = self.app.get(url, user=self.anonymous, status=403)
        self.assertEqual(response.status_code, 403)

        # Не владельцу доступ запрещен
        response = self.app.get(url, user=self.hacker, status=403)
        self.assertEqual(response.status_code, 403)

        # У админа есть доступ
        response = self.app.get(url, user=self.admin, status=200)
        self.assertEqual(response.status_code, 200)

        # У привязанных пользователей есть доступ
        response = self.app.get(url, user=self.owner)
        self.assertTemplateUsed(response, 'tourism/tour/add.html')
        self.assertEqual(response.context['firm'].pk, firm.pk)

        title = self.random_string(60)
        dates = '24.10.2011-30.10.2011'
        nights = self.random_string(30)
        price = 300000
        short = self.random_string(80)
        description = self.random_string(1000)

        form = response.forms['form-add-tour']
        form['title'] = title
        form['place'] = place.id
        form['dates'] = dates
        form['nights'] = nights
        form['price'] = str(price)
        form['short'] = short
        form['description'] = description

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/tour/moderate.html')

        tour = Tour.objects.get(title=title)
        tour_dates = TourDate.objects.filter(tour=tour)
        for tour_date in tour_dates:
            self.assertTrue(date(2011, 10, 24) <= tour_date.date <= date(2011, 10, 30))

        self.assertEqual(tour.title, title)
        self.assertEqual(tour.place, place)
        self.assertEqual(tour.nights, nights)
        self.assertEqual(tour.price, price)
        self.assertEqual(tour.short, short)
        self.assertTrue(tour.is_hidden)  # По умолчанию скрыт и ожидает модерации

    def test_edit_tour(self):
        """Редактирование тура"""

        firm = G(TourFirm, visible=True, section=[self.section, ], user=self.owner)
        place = G(Place)

        tour = G(Tour, is_hidden=True, firm=firm, file=None)

        url = '{0}?section={1}'.format(reverse('tourism:tour:edit', args=(tour.pk, )), self.section.slug)

        # Анонимам доступ запрещен
        response = self.app.get(url, user=self.anonymous, status=403)
        self.assertEqual(response.status_code, 403)

        # Не владельцу доступ запрещен
        response = self.app.get(url, user=self.hacker, status=403)
        self.assertEqual(response.status_code, 403)

        # У админа есть доступ
        response = self.app.get(url, user=self.admin, status=200)
        self.assertEqual(response.status_code, 200)

        # У привязанных пользователей есть доступ
        response = self.app.get(url, user=self.owner)
        self.assertTemplateUsed(response, 'tourism/tour/add.html')
        self.assertEqual(response.context['firm'].pk, firm.pk)

        title = self.random_string(60)
        dates = '24.10.2011-30.10.2011'
        nights = self.random_string(30)
        price = 300000
        short = self.random_string(80)
        description = self.random_string(1000)

        form = response.forms['form-add-tour']
        form['title'] = title
        form['place'] = place.id
        form['dates'] = dates
        form['nights'] = nights
        form['price'] = str(price)
        form['short'] = short
        form['description'] = description

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/tour/moderate.html')

        tour = Tour.objects.get(title=title)
        tour_dates = TourDate.objects.filter(tour=tour)
        for tour_date in tour_dates:
            self.assertTrue(date(2011, 10, 24) <= tour_date.date <= date(2011, 10, 30))

        self.assertEqual(tour.title, title)
        self.assertEqual(tour.place, place)
        self.assertEqual(tour.nights, nights)
        self.assertEqual(tour.price, price)
        self.assertEqual(tour.short, short)
        self.assertTrue(tour.is_hidden)  # После редактирования скрыт и ожидает модерации

        # Отправлять на модерацию только при изменении названия, описания или фотки

        # Не отправляется на модерацию
        tour.is_hidden = False
        tour.save()
        response = self.app.get(url, user=self.owner)
        price = 400000

        form = response.forms['form-add-tour']
        form['price'] = str(price)
        form.submit()

        tour = Tour.objects.get(title=title)

        self.assertEqual(tour.price, price)
        self.assertFalse(tour.is_hidden)

        # Отправляется на модерацию
        response = self.app.get(url, user=self.owner)
        price = 500000
        title = self.random_string(60)

        form = response.forms['form-add-tour']
        form['price'] = str(price)
        form['title'] = title
        form.submit()

        tour = Tour.objects.get(title=title)

        self.assertEqual(tour.price, price)
        self.assertEqual(tour.title, title)
        self.assertTrue(tour.is_hidden)

    def test_tour_read(self):
        """Страница тура"""

        firm = G(TourFirm, visible=True, section=[self.section, ], user=self.owner)

        tour = G(Tour, is_hidden=True, firm=firm, file=None)

        url = reverse('tourism:tour:read', args=(tour.pk, ))

        # История непромодерирована

        # Анонимам доступ запрещен
        response = self.app.get(url, user=self.anonymous, status=403)
        self.assertEqual(response.status_code, 403)

        # Не владельцу доступ запрещен
        response = self.app.get(url, user=self.hacker, status=403)
        self.assertEqual(response.status_code, 403)

        # Владельцу доступ разрешен
        response = self.app.get(url, user=self.owner)
        self.assertTemplateUsed(response, 'tourism/tour/read.html')
        context = response.context
        self.assertEqual(context['tour'], tour)
        self.assertTrue(context['can_edit'])
        self.assertEqual(context['related_firm'].pk, firm.pk)
        self.assertEqual(context['section'].pk, self.section.pk)

        # Админу доступ разрешен
        context = self.app.get(url, user=self.admin).context
        self.assertEqual(context['tour'], tour)
        self.assertTrue(context['can_edit'])
        self.assertEqual(context['related_firm'].pk, firm.pk)
        self.assertEqual(context['section'].pk, self.section.pk)

        # История промодерирована

        tour.is_hidden = False
        tour.save()
        self.app.session.flush()  # Очистка сессии модера из последнего запроса

        # Анонимам доступ разрешен
        context = self.app.get(url, user=None).context
        self.assertEqual(context['tour'], tour)
        self.assertFalse(context['can_edit'])
        self.assertEqual(context['related_firm'].pk, firm.pk)
        self.assertEqual(context['section'].pk, self.section.pk)

        # Не владельцу доступ разрешен
        context = self.app.get(url, user=self.hacker).context
        self.assertEqual(context['tour'], tour)
        self.assertFalse(context['can_edit'])
        self.assertEqual(context['related_firm'].pk, firm.pk)
        self.assertEqual(context['section'].pk, self.section.pk)

        # Владельцу доступ разрешен
        context = self.app.get(url, user=self.owner).context
        self.assertEqual(context['tour'], tour)
        self.assertTrue(context['can_edit'])
        self.assertEqual(context['related_firm'].pk, firm.pk)
        self.assertEqual(context['section'].pk, self.section.pk)

        # Админу доступ разрешен
        context = self.app.get(url, user=self.admin).context
        self.assertEqual(context['tour'], tour)
        self.assertTrue(context['can_edit'])
        self.assertEqual(context['related_firm'].pk, firm.pk)
        self.assertEqual(context['section'].pk, self.section.pk)

    def test_delete(self):
        """Удаление тура"""

        firm = G(TourFirm, visible=True, section=[self.section, ], user=self.owner)
        tour = G(Tour, is_hidden=True, firm=firm, file=None)

        url = reverse('tourism:tour:delete', args=(tour.pk, ))

        response = self.app.post(url, user=self.anonymous, status=302)
        self.assertEqual(response.status_code, 302)  # редирект для анонимов

        response = self.app.post(url, user=self.hacker, status=302)
        self.assertEqual(response.status_code, 302)  # редирект для непричастных

        response = self.app.post(url, user=self.owner).follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/firm/read.html')
        self.assertEqual(Tour.objects.filter(id=tour.id).exists(), False)
