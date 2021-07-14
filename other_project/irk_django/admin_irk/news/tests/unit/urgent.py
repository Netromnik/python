# -*- coding: utf-8 -*-

import unittest

from django.core.urlresolvers import reverse
from django_dynamic_fixture import get

from irk.tests.unit_base import UnitTestBase
from irk.news.models import UrgentNews


class IndexTestCase(UnitTestBase):
    """Проверка вывода срочной новости на индексе новостей"""

    # TODO неясно нужны ли строчные новости на индексе новостей
    @unittest.skip
    def test(self):
        url = reverse('news:index')

        context = self.app.get(url).context
        self.assertIsNone(context['urgent'])

        get(UrgentNews, is_visible=False)

        context = self.app.get(url).context
        self.assertIsNone(context['urgent'])

        instance = get(UrgentNews, is_visible=True)

        context = self.app.get(url).context
        self.assertEqual(instance, context['urgent'])

        instance.is_visible = False
        instance.save()

        context = self.app.get(url).context
        self.assertIsNone(context['urgent'])
