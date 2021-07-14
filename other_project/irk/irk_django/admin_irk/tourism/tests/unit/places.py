# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase
from irk.phones.models import MetaSection
from irk.tourism.models import Place, Tour
from irk.tourism.helpers import convent_place_type


class PlacesTestCase(UnitTestBase):
    """Тестирование мест туризма"""

    def setUp(self):
        super(PlacesTestCase, self).setUp()
        G(MetaSection, id=2)

    def test_index(self):
        """Индекс мест отдыха"""

        G(Place, is_main=True, parent=None, type=Place.BAIKAL, n=3)  # по умолчанию открываются места на Байкале
        response = self.app.get(reverse('tourism:places'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/place/list.html')
        self.assertEqual(len(response.context['objects']), 3)

    def test_place_categories(self):
        """Места отдыха по типам"""

        for slug in Place.TYPES_SLUG.values():
            place_type = convent_place_type(slug)
            G(Place, is_main=True, parent=None, type=place_type, n=3)
            response = self.app.get(reverse('tourism:places', args=(slug, )))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'tourism/place/list.html')

    def test_read(self):
        """Страница места отдыха"""

        slug = 'baikal'
        title = self.random_string(10)
        place = G(Place, title=title, parent=None, slug=slug, is_main=True)
        G(Tour, n=3, place=place, is_hidden=False)
        G(Tour, n=2, place=place, is_hidden=True)
        response = self.app.get(reverse('tourism:places', args=(slug, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/place/read_parent.html')
        self.assertEqual(response.context['place'].title, title)
        self.assertEqual(len(response.context['tours']), 3)

    def test_read_sub_place(self):
        """Страница подкатегории места отдыха"""

        title = self.random_string(10)
        parent_slug = 'baikal'
        slug = 'listvyanka'
        place = G(Place, title=title, parent=G(Place, parent=None, slug=parent_slug, is_main=True), slug=slug)
        G(Tour, n=3, place=place, is_hidden=False)
        G(Tour, n=2, place=place, is_hidden=True)
        response = self.app.get(reverse('tourism.views.place.sub_place', args=(parent_slug, slug)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tourism/place/read.html')
        self.assertEqual(response.context['place'].title, title)
        self.assertEqual(len(response.context['tours']), 3)