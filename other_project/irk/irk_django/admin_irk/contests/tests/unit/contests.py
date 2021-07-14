# -*- coding: UTF-8 -*-
from __future__ import absolute_import

from datetime import date, timedelta
from django_dynamic_fixture import G

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from irk.news.tests.unit.material import create_material
from irk.tests.unit_base import UnitTestBase

from irk.contests.models import Contest, Participant


class ContestsTest(UnitTestBase):
    """Тестирование конкурсов"""

    csrf_checks = False

    def test_participant_create(self):
        """Добавление участника в конкурс"""

        user = self.create_user('user', '123')
        today = date.today()
        tomorrow = today + timedelta(1)
        yesterday = today - timedelta(1)

        title = self.random_string(10)
        description = self.random_string(50)
        phone = self.random_string(20)

        # Участие в викторине
        contest = create_material(
            'contests', 'contest', date_start=yesterday, date_end=tomorrow, user_can_add=True, type='quiz',
            is_hidden=False
        )

        response = self.app.get(reverse('contests:contests:participant_create', args=(contest.slug,)), user=user)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contests/participant/add/quiz.html')

        self.app.post(reverse('contests:participant_create', args=(contest.slug,)), {
            'title': title,
            'description': description,
            'phone': phone,
        }, user=user)

        participant = Participant.objects.filter(contest=contest)

        self.assertEqual(participant.count(), 1, "Participant is not created")

        # Участие в показухе
        contest = create_material(
            'contests', 'contest', date_start=yesterday, date_end=tomorrow, user_can_add=True, is_hidden=False
        )
        self.app.post(reverse('contests:participant_create', args=(contest.slug,)), {
            'title': title,
            'description': description,
            'phone': phone,
            'gallerypicture_set-TOTAL_FORMS': 48,
            'gallerypicture_set-INITIAL_FORMS': 0,
            'gallerypicture_set-MAX_NUM_FORMS': 48,
        }, user=user)

        participant = Participant.objects.filter(contest=contest)

        self.assertEqual(participant.count(), 1, "Participant is not created")

    def test_participant(self):
        """Вывод участника в конкурса"""

        today = date.today()
        tomorrow = today + timedelta(1)
        yesterday = today - timedelta(1)

        contest = create_material(
            'contests', 'contest', date_start=yesterday, date_end=tomorrow, user_can_add=True
        )
        participant1 = G(Participant, n=1, contest=contest, is_active=True)
        participant2 = G(Participant, n=1, contest=contest, is_active=True)
        participant3 = G(Participant, n=1, contest=contest, is_active=True)
        G(Participant, n=5, contest=contest, is_active=True)
        response = self.app.get(reverse('contests:participant_read', args=(contest.slug, participant2.pk)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contests/participant/read.html')

        self.assertEqual(response.context['object'], participant2, "Variable object is wrong")
        self.assertEqual(response.context['previous'], participant1, "Variable previous is wrong")
        self.assertEqual(response.context['next'], participant3, "Variable next is wrong")
        self.assertEqual(len(response.context['other']), 4, "Wrong count of item in variable other")
        for participant in response.context['other']:
            self.assertTrue(isinstance(participant, Participant), "Variable other has wrong type")

    def test_index(self):
        """Вывод главной страницы конкурсов"""

        today = date.today()
        tomorrow = today + timedelta(1)
        yesterday = today - timedelta(1)
        month_ago = today - timedelta(30)

        create_material('contests', 'contest', date_start=yesterday, date_end=tomorrow, is_hidden=False, n=15)
        create_material('contests', 'contest', date_start=month_ago, date_end=yesterday, is_hidden=False, n=30)

        response = self.app.get(reverse('contests.views.index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contests/list.html')

        self.assertEqual(len(response.context['opened']), 10, "Variable opened has wrong item count")
        for contest in response.context['opened']:
            self.assertTrue(isinstance(contest, Contest), "Item of variable opened has wrong type")

        self.assertTrue(isinstance(response.context['paginator'], Paginator), "Variable closed not paginator")
        self.assertEqual(len(response.context['closed']), 10, "Variable closed has wrong item count")
        for contest in response.context['closed']:
            self.assertTrue(isinstance(contest, Contest), "Item of variable closed has wrong type")

    def test_read(self):
        """Вывод страницы конкурса"""

        today = date.today()
        tomorrow = today + timedelta(1)
        yesterday = today - timedelta(1)

        contest = create_material('contests', 'contest', n=1, date_start=yesterday, date_end=tomorrow)
        G(Participant, n=5, contest=contest, is_active=True)
        G(Participant, n=5, contest=contest, is_active=False)

        response = self.app.get(reverse('contests:contests:read', args=(contest.slug,)))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contests/read.html')

        self.assertEqual(response.context['object'], contest, "Variable object is wrong")

        self.assertEqual(len(response.context['participants']), 5, "Variable participants has wrong item count")
        for participant in response.context['participants']:
            self.assertTrue(isinstance(participant, Participant), "Item of variable Participant has wrong type")
