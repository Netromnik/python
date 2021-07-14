# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime

from django_dynamic_fixture import G
from django.core.urlresolvers import reverse

from irk.news.tests.unit.material import create_material
from irk.contests.models import Contest, Participant
from irk.tests.unit_base import UnitTestBase
from irk.options.models import Site


class ContestsTest(UnitTestBase):
    """Тестирование конкурсов"""

    def setUp(self):
        super(ContestsTest, self).setUp()
        self.site = Site.objects.get(slugs='obed')

    def test_index(self):
        """Индекс"""

        create_material('contests', 'contest', is_hidden=False, sites=[self.site], n=4)
        url = reverse('obed:contests:list')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/contests/list.html')

    def test_contest_read(self):
        """Конкретный конкурс"""

        contest = create_material('contests', 'contest', is_hidden=False, sites=[self.site])
        url = reverse('obed:contests:read', kwargs={'slug': contest.slug})
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/contests/read.html')

    def test_participant_read(self):
        """Участник конкурса"""

        contest = create_material('contests', 'contest', is_hidden=False, sites=[self.site])
        participant = G(Participant, contest=contest, is_active=True)
        url = reverse('obed:contests:participant_read', kwargs={'slug': contest.slug, 'participant_id': participant.id})
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/contests/participant/read.html')

    def test_participant_create(self):
        """Добавление участника в конкурс"""

        today = datetime.datetime.today()
        contest = create_material('contests', 'contest', is_hidden=False, date_start=today, date_end=today,
                                  sites=[self.site, ], type=Contest.TYPE_PHOTO)
        user = self.create_user('vasya')
        url = reverse('obed:contests:participant_create', kwargs={'slug': contest.slug})

        response = self.app.get(url, user=user)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/contests/participant/add/photo.html')

        contest.type = Contest.TYPE_QUIZ
        contest.save()
        response = self.app.get(url, user=user)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/contests/participant/add/quiz.html')
