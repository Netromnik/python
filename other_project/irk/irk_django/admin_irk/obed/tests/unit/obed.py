# -*- coding: UTF-8 -*-
from __future__ import absolute_import

from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase


class ObedTestCase(UnitTestBase):
    """"""

    def test_search(self):
        """"""

        response = self.app.get(reverse('obed:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/search_result.html')
