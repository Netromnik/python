# -*- coding: utf-8 -*-

from datetime import datetime

from django_dynamic_fixture import G

from irk.home.models import Logo

from irk.tests.unit_base import UnitTestBase


class OptionsTemplatetagsTest(UnitTestBase):
    """Тестирование шаблонных тегов"""

    def test_get_logo(self):
        """Тест функции get_logo"""

        from irk.options.templatetags.options import get_logo

        # Текущая дата, Дата начала, Дата окончания, Ожидамый результат
        dates = (
            ('2013-02-15', '02-10', '02-28', True),
            ('2013-02-15', '01-20', '02-28', True),
            ('2013-02-15', '02-15', '02-15', True),
            ('2013-02-15', '01-01', '12-21', True),
            ('2013-01-01', '12-28', '01-03', True),
            ('2013-02-15', '02-16', '02-14', False),
            ('2013-02-13', '03-16', '02-14', True),
            ('2013-02-15', '01-01', '02-14', False),
            ('2013-02-15', '02-16', '02-28', False),
            ('2013-02-15', '12-01', '12-31', False),
        )

        for date_item in dates:

            start_month = int(date_item[1].split('-')[0])
            start_day = int(date_item[1].split('-')[1])
            end_month = int(date_item[2].split('-')[0])
            end_day = int(date_item[2].split('-')[1])

            G(Logo, start_month=start_month, start_day=start_day, end_month=end_month, end_day=end_day, visible=True)

            cur_date = datetime.strptime(date_item[0], '%Y-%m-%d').date()

            self.assertEqual(bool(get_logo(cur_date)), date_item[3], "Failed test for (%s, %s, %s)" % (date_item[0], date_item[1], date_item[2]))

            Logo.objects.all().delete()
