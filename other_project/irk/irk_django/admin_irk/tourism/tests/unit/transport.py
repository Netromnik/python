# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django_dynamic_fixture import get, G
from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase
from irk.phones.models import MetaSection
from irk.transport.models import ElectricTrain, ElectricTrainTicket, Train, SuburbanBus


class TransportTestCase(UnitTestBase):
    """Тестирование транспортных страниц туризма"""

    def setUp(self):
        super(TransportTestCase, self).setUp()
        get(MetaSection, id=2)

    def test_etrains(self):
        """Расписание электричек"""

        url = reverse('tourism:transport_etrains')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/transport/etrains_online.html')
        G(ElectricTrain, n=5)
        response = self.app.get(url, params={'direction': 'east'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/transport/etrains.html')
        self.assertEqual(len(response.context['etrains']), 5)

    def test_etrains_tickets(self):
        """Цена билетов на электрички"""

        G(ElectricTrainTicket, n=5)
        response = self.app.get(reverse('tourism:transport_etrains_tickets'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/transport/etrains_tickets.html')
        self.assertEqual(len(response.context['tickets']), 5)

    def test_trains(self):
        """Расписание поездов"""

        url = reverse('tourism:transport_trains')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/transport/trains_online.html')
        G(Train, n=5)
        response = self.app.get(url, params={'direction': 'east'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/transport/trains.html')
        self.assertEqual(len(response.context['trains']), 5)

    def test_suburban(self):
        """Пригородные автобусы"""

        G(SuburbanBus, n=5)
        response = self.app.get(reverse('tourism.views.transp.transport_suburban'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/transport/suburban.html')
        self.assertEqual(len(response.context['autobuses']), 5)

    def test_gardening(self):
        """Дачные автобусы"""

        G(SuburbanBus, type=SuburbanBus.TYPE_GARDENING, n=5)
        response = self.app.get(reverse('tourism.views.transp.transport_gardening'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/transport/gardening.html')
        self.assertEqual(len(response.context['gardening']), 5)

    def test_airport(self):
        """Табо аэропорта"""

        response = self.app.get(reverse('tourism:airport'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/air_board.html')
