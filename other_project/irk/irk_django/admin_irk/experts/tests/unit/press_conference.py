# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import datetime

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.news.tests.unit.material import create_material
from irk.tests.unit_base import UnitTestBase

from irk.experts.models import Question


class PressConferenceTest(UnitTestBase):
    """Тестирование прессух"""

    csrf_checks = False

    def setUp(self):
        super(PressConferenceTest, self).setUp()
        self.author = self.create_user('expert2009')
        self.expert = create_material(
            'experts', 'expert', user=self.author, stamp_end=datetime.datetime.today(), is_consultation=False
        )
        G(Question, expert=self.expert, same_as=None, n=5)
        self.kwargs_ = {
            'category_alias': self.expert.category.slug,
            'expert_id': self.expert.id,
        }

    def test_expert_page(self):
        """Страница эксперта"""

        response = self.app.get(reverse('news:experts:read', kwargs=self.kwargs_))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'experts/read.html')
        self.assertEquals(len(response.context['objects']), 5)

    def test_ask_question(self):
        """Задать вопрос"""

        user = self.create_user('vasya3')
        question = 'Do you have a dog?'

        response = self.app.post(reverse('news:experts:question_create', kwargs=self.kwargs_),
                                 {'question': question}, user=user).follow()

        self.assertTemplateUsed(response, 'experts/read.html')
        questions = response.context['objects']
        self.assertEquals(question, questions[0].question)  # Добавленный через форму вопрос первый в списке
        self.assertEquals(len(questions), 6)
        self.assertIn(question, response.body)

    def test_reply_question(self):
        """Ответить на вопрос"""

        user = self.create_user('vasya3')
        question = G(Question, expert=self.expert, answer='')
        answer = self.random_string(30)
        params = {
            'answer': answer,
            'action': 'reply',
            'question': question.id,
            'gallerypicture_set-TOTAL_FORMS': 48,
            'gallerypicture_set-INITIAL_FORMS': 0,
            'gallerypicture_set-MAX_NUM_FORMS': 48,
        }
        response = self.app.post(reverse('news:experts:question_reply', kwargs=self.kwargs_),
                                 params, user=user, status='*')
        self.assertEquals(response.status_code, 403)  # Не ведущий отвечать не может

        response = self.app.post(reverse('news:experts:question_reply', kwargs=self.kwargs_),
                                 params, user=self.author).follow()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'experts/read.html')
        self.assertEqual(answer, Question.objects.get(pk=question.id).answer)  # Ответ сохранился

    def test_delete_question(self):
        """Удалить вопрос"""

        user = self.create_user('admin', is_admin=True)  # Удалять может модератор или админ
        question = G(Question, expert=self.expert)
        kwargs_ = self.kwargs_
        kwargs_['question_id'] = question.id
        question_cnt = Question.objects.filter(expert=self.expert).count()

        response = self.app.post(reverse('news:experts:question_delete', kwargs=self.kwargs_),
                                 user=user).follow()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'experts/read.html')
        new_question_cnt = Question.objects.filter(expert=self.expert).count()
        self.assertEqual(question_cnt-1, new_question_cnt)  # Один вопрос был удален
