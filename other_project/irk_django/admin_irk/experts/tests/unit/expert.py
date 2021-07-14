# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import datetime

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase
from irk.news.models import Category
from irk.news.tests.unit.material import create_material


class PressConferenceTest(UnitTestBase):
    """Тестирование страниц эксперта"""

    def setUp(self):
        super(PressConferenceTest, self).setUp()
        today = datetime.datetime.today()

        self.category = G(Category, slug='society')
        create_material(
            'experts', 'expert', category=self.category, stamp=today, stamp_end=today + datetime.timedelta(days=12),
            is_hidden=False, n=8
        )

    def test_expert_index(self):
        """Открытие индекса эксперта"""

        response = self.app.get(reverse('news:experts:index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'experts/index.html')
        self.assertEquals(len(response.context['expert_list']), 8)
