# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import json
import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from irk.news.tests.unit.material import create_material
from irk.contests.models import Participant
from irk.tests.unit_base import UnitTestBase
from irk.comments.models import Comment
from irk.ratings.models import RatingObject


class RatingTestCase(UnitTestBase):
    """Тесты рейтингов"""

    csrf_checks = False

    def setUp(self):
        super(RatingTestCase, self).setUp()
        self.anonymous = self.create_anonymous_user()
        self.user = self.create_user('vasya')
        self.unverified_user = self.create_user('petya', is_verified=False)
        self.url = reverse('ratings:rate')
        self.ct = ContentType.objects.get_for_model(Comment)
        self.comment = G(Comment)
        self.params = {
            'ct': self.ct.id,
            'value': 1,
            'obj': self.comment.id,
        }

    def test_rate(self):
        """Нормальный юзер плюсует"""

        G(RatingObject, content_type=self.ct, object_pk=self.comment.pk, total_cnt=1)

        self.app.post(self.url, params=self.params, user=self.user).follow()
        self.assertEqual(RatingObject.objects.get(content_type=self.ct, object_pk=self.comment.pk).total_cnt, 2)

        self.app.post(self.url, params=self.params, user=self.unverified_user).follow()
        self.assertEqual(RatingObject.objects.get(content_type=self.ct, object_pk=self.comment.pk).total_cnt, 2)

    def test_ajax_rate(self):
        """Нормальный юзер плюсует ajax-ом"""

        G(RatingObject, content_type=self.ct, object_pk=self.comment.pk, total_cnt=1)

        data = self.app.post(self.url, params=self.params, user=self.user,
                             headers={'X-Requested-With': 'XMLHttpRequest'})
        data = json.loads(data.content)

        self.assertEqual(data['status'], 200)
        self.assertEqual(RatingObject.objects.get(content_type=self.ct, object_pk=self.comment.pk).total_cnt, 2)

        self.app.post(self.url, params=self.params, user=self.unverified_user).follow()
        self.assertEqual(RatingObject.objects.get(content_type=self.ct, object_pk=self.comment.pk).total_cnt, 2)

    def test_anonymous_rate(self):
        """Плюсует аноним"""

        G(RatingObject, content_type=self.ct, object_pk=self.comment.pk, total_cnt=1)

        response = self.app.post(self.url, params=self.params, user=self.anonymous)
        self.assertEqual(response.status_code, 302)
        response = response.follow()
        self.assertTemplateUsed(response, 'auth/login.html')  # редирект на форму авторизации
        self.assertEqual(RatingObject.objects.get(content_type=self.ct, object_pk=self.comment.pk).total_cnt, 1)

    def test_banned_rate(self):
        """Плюсует забаненый"""

        banned_user = self.create_user('lament')
        banned_user.profile.is_banned = True
        banned_user.profile.save()

        G(RatingObject, content_type=self.ct, object_pk=self.comment.pk, total_cnt=1)
        self.app.post(self.url, params=self.params, user=banned_user).follow()

        # Голос не засчитался
        self.assertEqual(RatingObject.objects.get(content_type=self.ct, object_pk=self.comment.pk).total_cnt, 1)

    def test_bad_rate_value(self):
        """Пытаемся накрутить рейтинг неправильными значениями"""

        G(RatingObject, content_type=self.ct, object_pk=self.comment.pk, total_cnt=1)
        params = self.params
        params['value'] = 2
        response = self.app.post(self.url, params=params, user=self.user, status='*')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(RatingObject.objects.get(content_type=self.ct, object_pk=self.comment.pk).total_cnt, 1)

    def test_closed_rating(self):
        """Пытаемся голосовать за участника конкурса, где закрыто голосование"""

        contest = create_material('contests', 'contest', is_hidden=False)
        ct = ContentType.objects.get_for_model(Participant)
        participant = G(Participant, contest=contest, is_active=True)
        G(RatingObject, content_type=ct, object_pk=participant.pk, total_cnt=1)
        params = {
            'ct': ct.id,
            'value': 1,
            'obj': participant.id,
        }
        response = self.app.post(self.url, params=params, user=self.user, status='*')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(RatingObject.objects.get(content_type=ct, object_pk=participant.pk).total_cnt, 1)

        # Открываем конкурс, указав актуальные даты проведения конкурса
        participant.contest.date_start = datetime.datetime.today()
        participant.contest.date_end = datetime.datetime.today()
        participant.contest.save()

        response = self.app.post(self.url, params=params, user=self.user).follow()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RatingObject.objects.get(content_type=ct, object_pk=participant.pk).total_cnt, 2)  # Like+

    def test_rate_yourself_object(self):
        """Голосуем за свой же коммент"""

        comment = G(Comment, user=self.user)
        G(RatingObject, content_type=self.ct, object_pk=comment.pk, total_cnt=1)
        params = self.params
        params['obj'] = comment.id

        self.app.post(self.url, params=params, user=self.user)
        self.assertEqual(RatingObject.objects.get(content_type=self.ct, object_pk=comment.pk).total_cnt, 1)
