# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os

from datetime import date, timedelta

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.about.models import Page, Pricefile, Employee, Vacancy, Question, Faq, Condition, Section, \
    Interest, AgeGenderPercent
from irk.about.forms import AnonymousFeedbackForm, AuthFeedbackForm

from irk.tests.unit_base import UnitTestBase


class AboutTest(UnitTestBase):
    """О компании"""

    csrf_checks = False

    def setUp(self):
        self.general_section = G(Section, in_audience=True, in_mediakit=True, is_general=True)

    def _test_section_menu(self, url):
        """Тестирование вывода менюшки разделов"""

        G(Section, in_audience=False, in_mediakit=False, is_general=False)

        order = [2, 1, 4, 3, 6, 5, 7, 8]
        for position in order:
            G(Section, position=position, in_audience=True, in_mediakit=True, is_general=False)

        response = self.app.get(url)

        self.assertEqual(response.context['general_section'], self.general_section)
        self.assertEqual(len(response.context['sections']), 4)  # 4 колонки

        sections = []
        for column in response.context['sections']:
            sections.extend(column)
            self.assertEqual(len(column), 2)  # 2 элемента в колонке
        # Проверка правильности сортировки
        self.assertListEqual([x.position for x in sections], sorted(order))

    def _test_prices(self, url):
        """Тестирование контекста прайсов"""

        G(Page, n=13, visible=False, device=Page.ON_MOBILE)
        pages = G(Page, n=14, visible=True, device=Page.ON_MOBILE)

        response = self.app.get(url)

        self.assertEqual(response.context['devices'], Page.DEVICE_CHOICES)
        self.assertEqual(len(response.context['pages'][Page.ON_MOBILE][0]), 4)
        self.assertEqual(len(response.context['pages'][Page.ON_MOBILE][1]), 4)
        self.assertEqual(len(response.context['pages'][Page.ON_MOBILE][2]), 3)
        self.assertEqual(len(response.context['pages'][Page.ON_MOBILE][3]), 3)
        self.assertTrue(isinstance(response.context['pages'][Page.ON_MOBILE][0][0], Page))
        self.assertTrue(response.context['pages'][Page.ON_MOBILE][0][0], pages[0])

    def _test_charts(self, section, url):
        """Тестирование контекста графиков"""

        interest1 = G(Interest, section=section, percent=10)
        interest2 = G(Interest, section=section, percent=30)
        interest3 = G(Interest, section=section, percent=20)

        agpm24 = G(AgeGenderPercent, age=AgeGenderPercent.AGE_18_24, gender=AgeGenderPercent.GENDER_MAN, percent=20,
                   section=section)
        agpw24 = G(AgeGenderPercent, age=AgeGenderPercent.AGE_18_24, gender=AgeGenderPercent.GENDER_WOMAN, percent=25,
                   section=section)
        agpm18 = G(AgeGenderPercent, age=AgeGenderPercent.AGE_18, gender=AgeGenderPercent.GENDER_MAN, percent=5,
                   section=section)
        agpw18 = G(AgeGenderPercent, age=AgeGenderPercent.AGE_18, gender=AgeGenderPercent.GENDER_WOMAN, percent=10,
                   section=section)
        agpm34 = G(AgeGenderPercent, age=AgeGenderPercent.AGE_25_34, gender=AgeGenderPercent.GENDER_MAN, percent=3,
                   section=section)
        agpw34 = G(AgeGenderPercent, age=AgeGenderPercent.AGE_25_34, gender=AgeGenderPercent.GENDER_WOMAN, percent=35,
                   section=section)

        context = self.app.get(url).context

        self.assertEqual(context['common_gender_man_percent'],
                         agpm18.percent + agpm24.percent + agpm34.percent)
        self.assertEqual(context['common_gender_woman_percent'],
                         agpw18.percent + agpw24.percent + agpw34.percent)

        # Тестирование сортировки интересов
        self.assertEqual(context['ratio_interests'][0]['object'], interest2)
        self.assertEqual(context['ratio_interests'][1]['object'], interest3)
        self.assertEqual(context['ratio_interests'][2]['object'], interest1)

        # Тестирование сортировки распределения по возрастам
        self.assertEqual(context['agegenderpercents_grouped'][AgeGenderPercent.AGE_18][0]['object'], agpm18)
        self.assertEqual(context['agegenderpercents_grouped'][AgeGenderPercent.AGE_18][1]['object'], agpw18)
        self.assertEqual(context['agegenderpercents_grouped'][AgeGenderPercent.AGE_18_24][0]['object'], agpm24)
        self.assertEqual(context['agegenderpercents_grouped'][AgeGenderPercent.AGE_18_24][1]['object'], agpw24)
        self.assertEqual(context['agegenderpercents_grouped'][AgeGenderPercent.AGE_25_34][0]['object'], agpm34)
        self.assertEqual(context['agegenderpercents_grouped'][AgeGenderPercent.AGE_25_34][1]['object'], agpw34)

    def test_prices(self):
        """Прайс-лист компании"""

        url = reverse('about:prices')

        G(Pricefile, slug='test')
        pricefile = G(Pricefile, slug='mainprice')
        G(Employee, is_op=True)
        G(Employee, is_op=False)
        employee = G(Employee, is_head_op=True)

        response = self.app.get(url)

        self.assertEqual(response.context['pricefile'], pricefile)
        self.assertEqual(response.context['employee_head_op'], employee)

        self._test_prices(url)

    def test_feedback(self):
        """Форма отзывов"""

        #TODO тестировать рассылку писем

        url = reverse('about:feedback')
        user = self.create_user('user', '123')

        response = self.app.get(url)
        self.assertTrue(isinstance(response.context['form'], AnonymousFeedbackForm))
        self.assertFalse(response.context['is_sent'])

        response = self.app.get(url, user=user)
        self.assertTrue(isinstance(response.context['form'], AuthFeedbackForm))
        self.assertFalse(response.context['is_sent'])

        # Тестирование отправки файла
        content = self.random_string(1024)
        attach_content = self.random_string(1024)
        form = response.forms['idFormFeedback']
        form['content'] = content
        form['attach_0'] = 'test_file.doc', attach_content
        response = form.submit()
        self.assertTrue(response.context['is_sent'])

        question = Question.objects.all()[0]
        attach_content_open = open(question.attach.path, 'r').read()
        self.assertEqual(question.content, content)
        self.assertEqual(attach_content_open, attach_content)
        os.remove(question.attach.path)

    def test_about_us(self):
        """Медиакиты"""

        url = reverse('about:about_us')
        G(Employee, is_op=False, n=3)

        order = [2, 1, 4, 3]
        for position in order:
            G(Employee, is_op=True, position=position)

        response = self.app.get(url)
        self.assertTemplateUsed(response, 'about/about_us.html')
        self.assertEqual(len(response.context['employees_op']), 4)
        self.assertEqual(len(response.context['employees']), 3)
        self.assertListEqual([x.position for x in response.context['employees_op']], sorted(order))

    def test_about_us_vacancy(self):
        """Список вакансий"""

        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(1)

        G(Vacancy, n=5, end_date=yesterday)
        G(Vacancy, n=4, end_date=None)
        G(Vacancy, n=3, end_date=today)
        G(Vacancy, n=2, end_date=tomorrow)

        response = self.app.get(reverse('about:about_us'))

        self.assertEqual(len(response.context['vacancies']), 9)

    #TODO Сделать!
    def test_example(self):
        """Примеры компаний"""
        url = reverse('about:example')
        response = self.app.get(url)
        self.assertTemplateUsed(response, 'about/example.html')

    def test_mediakit(self):
        """Медиакит"""

        section = G(Section, in_mediakit=True, slug='home')

        G(Employee, is_op=True)
        G(Employee, is_op=False)
        employee = G(Employee, is_head_op=True)

        url = reverse('about:mediakit', kwargs={'mediakit_id': section.pk})

        response = self.app.get(url)
        self.assertTemplateUsed(response, 'about/mediakit/read.html')
        self.assertEqual(response.context['section'], section)
        self.assertEqual(response.context['employee_head_op'], employee)

        self._test_charts(section, url)

    def test_mediakit_pdf(self):
        """Медиакит PDF"""

        section = G(Section, in_mediakit=True, slug='home')

        url = reverse('about:mediakit_pdf', kwargs={'mediakit_id': section.pk})

        response = self.app.get(url)
        self.assertTemplateUsed(response, 'about/mediakit/read_pdf.html')
        self.assertEqual(response.context['section'], section)
        self.assertEqual(response['Content-Type'], 'application/pdf')

        self._test_charts(section, url)

    def test_mediakits(self):
        """Медиакиты"""

        url = reverse('about:mediakits')

        response = self.app.get(url)

        self.assertTemplateUsed(response, 'about/mediakit/list.html')
        self._test_section_menu(url)

    def test_audiences(self):
        """Аудитории"""

        url = reverse('about:audiences')
        response = self.app.get(url)
        self.assertTemplateUsed(response, 'about/audience/list.html')
        self._test_section_menu(url)

    def test_audience(self):
        """Аудитория"""

        params = {
            'view_count_day': 1,
            'view_count_week': 1,
            'view_count_month': 1,
            'unique_user_count_day': 1,
            'unique_user_count_week': 1,
            'unique_user_count_month': 1
        }

        page_pc = G(Page, visible=True, device=Page.ON_PC, **params)
        page_mobile = G(Page, visible=True, device=Page.ON_MOBILE, **params)

        section = G(Section, in_audience=True, pages=[page_pc, page_mobile])

        url = reverse('about:audience', kwargs={'audience_id': section.pk})
        response = self.app.get(url)

        self.assertTemplateUsed(response, 'about/audience/read.html')
        self.assertEqual(response.context['section'], section)
        self.assertEqual(response.context['view_count_day'], 2)
        self.assertEqual(response.context['view_count_week'], 2)
        self.assertEqual(response.context['view_count_month'], 2)
        self.assertEqual(response.context['unique_user_count_day'], 2)
        self.assertEqual(response.context['unique_user_count_week'], 2)
        self.assertEqual(response.context['unique_user_count_month'], 2)

        self._test_charts(section, url)

    def test_faq(self):
        """Страница FAQ"""

        url = reverse('about:faq')

        order = [2, 1, 4, 3]
        for position in order:
            G(Faq, position=position)

        response = self.app.get(url)
        self.assertTemplateUsed(response, 'about/faq.html')
        self.assertListEqual([x.position for x in response.context['faqs']], sorted(order))

    def test_condition(self):
        """Страница требований к рекламе"""

        url = reverse('about:condition')

        order = [2, 1, 4, 3]
        for position in order:
            G(Condition, position=position)

        response = self.app.get(url)
        self.assertTemplateUsed(response, 'about/conditions.html')
        self.assertListEqual([x.position for x in response.context['conditions']], sorted(order))
