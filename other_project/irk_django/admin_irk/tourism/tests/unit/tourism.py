# -*- coding: UTF-8 -*-
from __future__ import absolute_import

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.news.tests.unit.material import create_material
from irk.obed.models import ArticleCategory
from irk.phones.models import MetaSection
from irk.tests.unit_base import UnitTestBase

from irk.tourism.models import Place


class TourismTest(UnitTestBase):
    """Тесты Туризма"""

    def setUp(self):
        super(TourismTest, self).setUp()
        G(MetaSection, id=2)

    def test_index(self):
        """Индекс"""

        G(MetaSection, id=1, alias='rent')
        G(Place, is_main=True, type=Place.LOCAL, n=3)
        G(Place, is_main=True, type=Place.EXTERNAL, n=3)
        section_category = G(ArticleCategory)
        create_material('tourism', 'article', is_hidden=False, section_category=section_category, n=2)
        create_material('tourism', 'article', is_hidden=True, section_category=section_category)

        response = self.app.get(reverse('tourism:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/index.html')
        self.assertEqual(len(response.context['places_local']), 3)
        self.assertEqual(len(response.context['places_foreign']), 3)
        self.assertEqual(len(response.context['blogs']), 2)

    def test_hotel_order(self):
        """Заказ отеля"""

        response = self.app.get(reverse('tourism:hotel_order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/hotel/order.html')

    def test_baikal_map(self):
        """Карта Байкала"""

        response = self.app.get(reverse('tourism.views.baikal_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/baikal/index.html')

    def test_search(self):
        """Поиск"""

        response = self.app.get(reverse('tourism:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/search_result.html')

    def test_aviasales(self):
        """Бронирование авиабилетов"""

        response = self.app.get(reverse('tourism:aviasales'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/aviasales.html')
