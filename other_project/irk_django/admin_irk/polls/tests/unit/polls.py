# -*- coding: utf-8 -*-

from __future__ import absolute_import

from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django_dynamic_fixture import G
from django_dynamic_fixture.fixture_algorithms.sequential_fixture import SequentialDataFixture

from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.polls.models import PollChoice, Poll, PollVote
from irk.tests.unit_base import UnitTestBase
from irk.utils.helpers import iptoint


class SequentialDataByYearFixture(SequentialDataFixture):
    # DATE/TIME RELATED
    def datefield_config(self, field, key):
        data = self.get_value(field, key)
        return date.today() - relativedelta(years=int(data))


class PollTest(UnitTestBase):
    """Тестирование голосований"""

    csrf_checks = False

    def setUp(self):
        self._site = Site.objects.filter(slugs="news").first()

    def test_index(self):
        """Главная страница голосований"""

        create_material(
            'polls', 'poll', n=3, data_fixture=SequentialDataByYearFixture(), target_ct=None, sites=[self._site],
            site=self._site
        )

        response = self.app.get(reverse('polls:index'))
        self.assertTemplateUsed(response, 'polls/index.html')

        self.assertEqual(len(response.context['years']), 3, "Wrong number of years")
        for year in response.context['years']:
            self.assertTrue(isinstance(year, date), "Variable years is not datetime")

    def test_year(self):
        """Список голосований за год"""

        end_date = date.today()
        start_date = end_date - relativedelta(years=3)

        create_material(
            'polls', 'poll', n=3, target_ct=None, start=start_date, end=end_date, site=self._site
        )

        response = self.app.get(reverse('polls:year', args=(start_date.year,)))
        self.assertTemplateUsed(response, 'polls/year.html')

        self.assertEqual(int(response.context['curr_year']), start_date.year, "Variable curr_year is broken")
        self.assertEqual(len(response.context['years']), 3, "Wrong number of years")
        for year in response.context['years']:
            self.assertTrue(isinstance(year, date), "Variable years is not datetime")

        self.assertEqual(len(response.context['polls']), 3, "Wrong number of polls")
        for poll in response.context['polls']:
            self.assertTrue(isinstance(poll, Poll), "Variable polls is not Poll object")

    def test_results(self):
        """Результаты голосования"""

        today = date.today()

        year = today.year - 2

        create_material('polls', 'poll', n=3, data_fixture=SequentialDataByYearFixture(), site=self._site)

        poll = Poll.objects.all()[1]
        response = self.app.get(reverse('polls:results', args=(year, poll.pk)))
        self.assertTemplateUsed(response, 'polls/result.html')

        self.assertEqual(response.context['today'], today, "Variable today is broken")
        self.assertEqual(response.context['poll'], poll, "Variable poll is broken")
        self.assertEqual(len(response.context['years']), 3, "Wrong number of years")
        self.assertFalse(response.context['arh_link'], "Variable arh_link is broken")
        self.assertTrue(response.context['voted'], "Variable voted is broken")
        for year in response.context['years']:
            self.assertTrue(isinstance(year, date), "Variable years is not datetime")

    def test_ajax_results(self):
        """Результаты голосования ajax-ом"""

        today = date.today()

        year = today.year - 2

        create_material('polls', 'poll', n=3, data_fixture=SequentialDataByYearFixture(), site=self._site)

        poll = Poll.objects.all()[1]
        response = self.app.get(reverse('polls:results', args=(year, poll.pk)),
                                headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertTemplateUsed(response, 'polls/snippets/poll.html')

        self.assertEqual(response.context['today'], today, "Variable today is broken")
        self.assertEqual(response.context['poll'], poll, "Variable poll is broken")
        self.assertEqual(len(response.context['years']), 3, "Wrong number of years")
        self.assertFalse(response.context['arh_link'], "Variable arh_link is broken")
        self.assertTrue(response.context['voted'], "Variable voted is broken")
        for year in response.context['years']:
            self.assertTrue(isinstance(year, date), "Variable years is not datetime")

    def test_vote(self):
        """Голосование"""

        start_poll = date.today() - timedelta(10)
        end_poll = date.today() + timedelta(10)

        poll = create_material('polls', 'poll', start=start_poll, end=end_poll, site=self._site)
        choices = G(PollChoice, n=3, poll=poll)

        # Голосуем несколько раз
        self.app.post(reverse('polls:vote'), params={'poll': poll.pk, 'choice': choices[1].pk})
        self.app.post(reverse('polls:vote'), params={'poll': poll.pk, 'choice': choices[1].pk})
        self.app.post(reverse('polls:vote'), params={'poll': poll.pk, 'choice': choices[1].pk})

        poll_choice_2 = PollChoice.objects.all()[1]
        poll_vote = PollVote.objects.all()

        self.assertEqual(poll_vote.count(), 1, "Vote is not saved")
        self.assertEqual(poll_vote[0].choice, poll_choice_2, "Wrong choice in saved vote")
        self.assertEqual(poll_vote[0].ip, iptoint('127.0.0.1'), "Wrong ip in saved vote")

    def test_vote_ajax(self):
        """Голосование ajax"""

        today = date.today()

        start_poll = date.today() - timedelta(10)
        end_poll = date.today() + timedelta(10)

        poll = create_material('polls', 'poll', start=start_poll, end=end_poll, site=self._site)
        choices = G(PollChoice, n=3, poll=poll)

        # Голосуем несколько раз
        response = self.app.post(reverse('polls:vote'), params={'poll': poll.pk, 'choice': choices[1].pk},
                                 headers={'X-Requested-With': 'XMLHttpRequest'})
        self.app.post(reverse('polls:vote'), params={'poll': poll.pk, 'choice': choices[1].pk},
                      headers={'X-Requested-With': 'XMLHttpRequest'})
        self.app.post(reverse('polls:vote'), params={'poll': poll.pk, 'choice': choices[1].pk},
                      headers={'X-Requested-With': 'XMLHttpRequest'})

        poll_choice_2 = PollChoice.objects.all()[1]
        poll_vote = PollVote.objects.all()

        self.assertEqual(poll_vote.count(), 1, "Vote is not saved")
        self.assertEqual(poll_vote[0].choice, poll_choice_2, "Wrong choice in saved vote")
        self.assertEqual(poll_vote[0].ip, iptoint('127.0.0.1'), "Wrong ip in saved vote")

        self.assertEqual(response.context['poll'], poll, "Variable poll is broken")
        self.assertEqual(response.context['voted'], True, "Variable voted is broken")
        self.assertEqual(response.context['arh_link'], False, "Variable arh_link is broken")
        self.assertEqual(response.context['new'], False, "Variable new is broken")
        self.assertEqual(response.context['today'], today, "Variable today is broken")
        self.assertEqual(self.app.cookies, {'pl': str(poll.pk)}, "Cookies is broken")
