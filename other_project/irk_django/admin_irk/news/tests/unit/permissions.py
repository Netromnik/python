# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.contrib.auth.models import Permission

from irk.tests.unit_base import UnitTestBase

from irk.news.tests.unit.material import create_material


class CanSeeHiddenTest(UnitTestBase):
    """Тесты проверки разрешения «Может видеть скрытые»"""

    def test_default(self):
        """Проверка того, что пользователь с разрешением can_see_hidden может читать скрытые материалы"""

        material = create_material('news', 'news', is_hidden=True, slug=self.random_string(10).lower())

        user = self.create_user('user')
        response = self.app.get(material.get_absolute_url(), user=user, expect_errors=True)
        self.assertEqual(404, response.status_code)

        user_can_see = self.create_user('user_can_see')
        permission = Permission.objects.get(codename='can_see_hidden')
        user_can_see.user_permissions.add(permission)

        response = self.app.get(material.get_absolute_url(), user=user_can_see, expect_errors=True)
        self.assertStatusIsOk(response)
