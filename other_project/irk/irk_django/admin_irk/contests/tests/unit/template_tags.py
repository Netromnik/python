# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import datetime

from django import template
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase

from irk.contests.templatetags.contests_tags import ContestNode


class ContestsTemplateTagTest(UnitTestBase):
    """Шаблонный тег для вывода последнего конкурса привязанного к разделу"""

    def test_template_tag(self):
        """Блок конкурса в Афише"""

        afisha_site = Site.objects.get(slugs='afisha')
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(1)
        yesterday = today - datetime.timedelta(1)

        title = self.random_string(15)
        create_material(
            'contests', 'contest', title=title, sites=[afisha_site, ], date_start=yesterday, date_end=tomorrow
        )

        request = RequestFactory().get(reverse('afisha:index'))
        request.csite = afisha_site
        node = ContestNode(template='contests/tags/afisha_latest.html')
        context = template.Context({'request': request})
        response = node.render(context)

        # Конкурс вывелся
        self.assertIn(title, response)
