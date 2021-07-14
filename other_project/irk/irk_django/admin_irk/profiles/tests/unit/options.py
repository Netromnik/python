# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from irk.profiles.options import options_library
from irk.tests.unit_base import UnitTestBase


class SetOptionTest(UnitTestBase):
    """Тесты на установку опций"""

    @classmethod
    def setUpClass(cls):
        super(SetOptionTest, cls).setUpClass()
        # Регистрация пользовательских опций
        options_library.discovery()

    def setUp(self):
        self._url = reverse('profiles:set_option')
        self._user = self.create_user('user')

    def test_weathercity_default(self):
        """Проверка выбора городов в Погоде"""

        params = {
            'param': 'weather.weatherfavoritecity',
            'value': '15',
            'next': reverse('weather.views.index'),
        }

        response = self.app.get(self._url, params=params, user=self._user)

        self.assertEqual(302, response.status_code)
        self.assertIn(reverse('weather.views.index'), response.url)
