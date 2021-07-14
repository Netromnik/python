# -*- coding: UTF-8 -*-

from __future__ import absolute_import

import json

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase
from irk.experts.models import Expert


class SubscriptionTestCase(UnitTestBase):
    """Тестирование подписки на конференции"""

    csrf_checks = False

    def ajax_post(self, url, **kwargs):
        return self.app.post(url, headers={'X_REQUESTED_WITH': 'XMLHttpRequest'}, **kwargs)

    def test_subscription(self):
        """Подписка на конференции"""

        user = self.create_user('user')

        expert = G(Expert, )

        url = reverse('news:experts:subscription')

        response = self.app.post(url, params={'expert_id': expert.pk}, expect_errors=True)
        self.assertEqual(response.status_code, 403)

        response = self.app.get(url, params={'expert_id': expert.pk},
                                headers={'X_REQUESTED_WITH': 'XMLHttpRequest'}, expect_errors=True)
        self.assertEqual(response.status_code, 403)

        response = self.ajax_post(url, params={'id': expert.pk})
        answer = json.loads(response.content)
        self.assertEqual(answer['error'], u'Неверный формат почтового адреса')

        response = self.ajax_post(url, params={'id': expert.pk, 'email': 'example@example.com'})
        answer = json.loads(response.content)
        self.assertTrue(answer['success'])

        response = self.ajax_post(url, params={'id': 100500}, user=user, expect_errors=True)
        self.assertEqual(response.status_code, 400)

        response = self.ajax_post(url, params={'id': expert.pk}, user=user)
        answer = json.loads(response.content)
        self.assertTrue(answer['success'])
