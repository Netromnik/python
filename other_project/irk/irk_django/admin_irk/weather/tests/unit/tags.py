# -*- coding: UTF-8 -*-
from __future__ import absolute_import

from datetime import date

from django import template
from irk.tests.unit_base import UnitTestBase

from irk.weather.models import WeatherSigns
from irk.weather.templatetags.weather_tags import sign, WeatherSignNode


class WeatherTagsTest(UnitTestBase):
    """Тестирование шаблонных тэгов погоды"""

    def test_sign(self):
        """ Фильтр sign"""

        source_values = [0, 100, -100, +100, '0', '100', '-100', '+100']
        expected_values = ['0', '+100', '-100', '+100', '0', '+100', '-100', '+100']

        for idx, source_value in enumerate(source_values):
            self.assertEqual(sign(source_value), expected_values[idx],
                             "Filter sign fail on value with index %s" % str(idx))

    def test_weather_sign(self):
        """Тег weather_sign"""

        # Генерация примет на каждый день года
        for month in range(1, 13):
            for day in range(1, 32):
                text = '%s%s' % (day, month)
                weather_signs = WeatherSigns(month=month, day=day, text=text)
                weather_signs.save()

        # Определение текста текущего дня
        today = date.today()
        month = int(today.strftime('%m'))
        day = int(today.strftime('%d'))
        text = '%s%s' % (day, month)

        node = WeatherSignNode('sign')
        context = template.Context()
        node.render(context)

        self.assertEqual(context['sign'], text, 'Variable sign is wrong')
