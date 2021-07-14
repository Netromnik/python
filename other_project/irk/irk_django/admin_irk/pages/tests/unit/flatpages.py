# -*- coding: UTF-8 -*-
from __future__ import absolute_import

from django_dynamic_fixture import G

from irk.pages.models import Page
from irk.pages.settings import FLATPAGE_TEMPLATES

from irk.tests.unit_base import UnitTestBase
from irk.options.models import Site
from irk.phones.models import MetaSection


class FlatPagesTestCase(UnitTestBase):
    """Тесты простых страниц"""

    def test_index(self):
        """Проверка доступных шаблонов страниц"""

        # для блока форума в туризме
        G(MetaSection, id=1, alias='rent')
        G(MetaSection, id=2)
        site = Site.objects.get(slugs='home')
        for template in FLATPAGE_TEMPLATES:
            if 'landing' not in template[0]:  # У нас сложная для тестов логика у лэндингов с подключением стилей
                url = '/{0}/'.format(self.random_string(10).lower())
                page = G(Page, content=self.random_string(50), site=site,
                         url=url, template_name=template[0])
                response = self.app.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template[0])
                self.assertEqual(response.context['flatpage'].content, page.content)
