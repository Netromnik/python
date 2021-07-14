# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase
from irk.options.models import Site
from irk.phones.models import MetaSection
from irk.news.tests.unit.material import create_material


class InfographicTestCase(UnitTestBase):
    """Инфографика в Туризме"""

    def setUp(self):
        super(InfographicTestCase, self).setUp()

        # для блока форума в туризме
        G(MetaSection, id=1, alias='rent')
        G(MetaSection, id=2)

    def test_list(self):
        """Список"""

        site_tourism = Site.objects.get(slugs='tourism')
        site_news = Site.objects.get(slugs='news')
        url = reverse('tourism.views.infographic.index')

        response = self.app.get(url)
        self.assertTemplateUsed(response, 'tourism/infographic/index.html')
        self.assertEqual(0, len(response.context['object_list']))

        create_material('tourism', 'infographic', sites=[site_news, ], is_hidden=False)
        context = self.app.get(url).context
        self.assertEqual(0, len(context['object_list']))

        create_material('tourism', 'infographic', sites=[site_news, site_tourism], is_hidden=False)
        context = self.app.get(url).context
        self.assertEqual(1, len(context['object_list']))

    def test_read(self):
        """Страница инфографики"""

        site_ny = Site.objects.get(slugs='tourism')
        obj = create_material('tourism', 'infographic', sites=[site_ny, ], is_hidden=False)

        response = self.app.get(obj.get_absolute_url())
        self.assertTemplateUsed(response, 'tourism/infographic/read.html')
        self.assertEqual(obj, response.context['object'])
