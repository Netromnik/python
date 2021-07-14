# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import json
from django.core.urlresolvers import reverse
from irk.tests.unit_base import UnitTestBase


class SocialRegisterTestCase(UnitTestBase):
    """Авторизация через соц сети"""

    def test_social_error(self):
        """Ошибка при авторизации/регистрации через соц сети"""

        url = reverse('social:error')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/social/error.html')

        response = self.app.get(url, headers={'X_REQUESTED_WITH': 'XMLHttpRequest', })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 403)
