# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase
from irk.options.models import Site

from irk.news.forms import SubscriptionAnonymousForm
from irk.news.models import Subscriber
from irk.news.tests.unit.material import create_material


class SubscriptionTest(UnitTestBase):
    """Подписка на новости"""

    csrf_checks = False

    def setUp(self):
        super(SubscriptionTest, self).setUp()
        self.today = datetime.datetime.today()
        self.week_ago = self.today - datetime.timedelta(7)

    def test_anonymous_confirm_subscription(self):
        """Незарегестрированый пользователь подтверждает подписку"""

        subscriber = G(Subscriber, email='example2@example.com',  is_active=False, hash=self.random_string(40),
                       hash_stamp=self.today)
        subscriber_old = G(Subscriber, email='example1@example.com',  is_active=False, hash=self.random_string(40),
                           hash_stamp=self.week_ago)

        response = self.app.get('%s?hash=%s' % (reverse('news:subscription:confirm'), subscriber.hash),)
        self.assertTemplateUsed(response, 'news-less/subscription/success.html')
        subscriber = Subscriber.objects.get(email=subscriber.email)
        self.assertTrue(subscriber.is_active)

        # Незарегестрированый пользователь подтверждает старую подписку
        response = self.app.get('%s?hash=%s' % (reverse('news:subscription:confirm'), subscriber_old.hash),)
        self.assertTemplateUsed(response, 'news-less/subscription/expired.html')
        subscriber = Subscriber.objects.get(email=subscriber_old.email)
        self.assertFalse(subscriber.is_active)

    def test_anonymous_subscribe(self):
        """Пользователь не зарегестрирован"""

        response = self.app.get(reverse('news:subscription:index'))
        self.assertTemplateUsed(response, 'news-less/subscription/add.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], SubscriptionAnonymousForm)

    def test_user_with_subscription(self):
        """Пользователь уже имеет подписку"""

        user_subscribed = self.create_user('user1')
        subscriber = G(Subscriber, email='%s@example.com' % user_subscribed, user=user_subscribed,
                       is_active=True, hash=self.random_string(40), hash_stamp=self.today)

        response = self.app.get(reverse('news:subscription:index'), user=user_subscribed)
        self.assertTemplateUsed(response, 'news-less/subscription/unsubscribe_form.html')
        self.assertIn('subscriber', response.context)
        self.assertEquals(response.context['subscriber'], subscriber)

        # Зарегестрированый пользователь оформляет подписку
        # Почтовый ящик уже подписан
        response = self.app.post(reverse('news:subscription:index'), user=user_subscribed,
                                 params={'email': '%s@example.com' % user_subscribed})
        self.assertTemplateUsed(response, 'news-less/subscription/unsubscribe_form.html')
        self.assertIn('subscriber', response.context)
        self.assertEquals(response.context['subscriber'], subscriber)

    def test_user_without_subscription(self):
        """Пользователь зарегестрирован, подписки нет"""

        user_notsubscribed = self.create_user('user2')

        response = self.app.get(reverse('news:subscription:index'), user=user_notsubscribed)
        self.assertTemplateUsed(response, 'news-less/subscription/add.html')
        self.assertIn('email', response.context)
        self.assertEquals(response.context['email'], user_notsubscribed.email)

        #Почтовый ящик еще не подписан
        response = self.app.post(reverse('news:subscription:index'), user=user_notsubscribed,
                                 params={'email': '%s@example.com' % user_notsubscribed})

        self.assertTemplateUsed(response, 'news-less/subscription/success.html')
        subscriber = Subscriber.objects.get(email=user_notsubscribed.email)
        self.assertEquals(subscriber.email, user_notsubscribed.email)
        self.assertTrue(subscriber.is_active,)
        self.assertEquals(subscriber.user, user_notsubscribed)

    def test_user_unsubscribe(self):
        """Отписаться от рассылки"""

        user_subscribed = self.create_user('user1')
        subscriber = G(Subscriber, email='%s@example.com' % user_subscribed, user=user_subscribed,
                       is_active=True, hash=self.random_string(40), hash_stamp=self.today)
        params = {
            'hash': subscriber.hash,
            'mail': subscriber.email,
        }
        response = self.app.get(reverse('news:subscription:unsubscribe'), params)
        self.assertTemplateUsed(response, 'news-less/subscription/unsubscribe_confirm.html')
        self.assertEqual(response.context['email'], subscriber.email)

        params['remove'] = True
        self.assertEqual(Subscriber.objects.filter(email=subscriber.email).exists(), True)

        response = self.app.post(reverse('news:subscription:unsubscribe'), params)

        self.assertTemplateUsed(response, 'news-less/subscription/unsubscribe_ok.html')
        self.assertEqual(Subscriber.objects.filter(email=subscriber.email).exists(), False)


class SubscriptionAjaxTest(UnitTestBase):
    """Подписка на новости через ajax"""

    csrf_checks = False

    def setUp(self):
        self.url = reverse('news:subscription:ajax')

    def test_when_not_email(self):
        """Нет поля email"""

        data = {
            'labuda': 'demo@example.com',
        }

        response = self.ajax_post(self.url, data)

        self.assertFalse(response.json['ok'])

    def test_when_email_invalid(self):
        """Неправильный email"""

        data = {
            'email': 'labuda',
        }

        response = self.ajax_post(self.url, data)

        self.assertFalse(response.json['ok'])

    def test_default(self):
        """Стандартное поведение"""

        data = {
            'email': 'demo@example.com',
        }

        response = self.ajax_post(self.url, data)

        self.assertTrue(response.json['ok'])
        self.assertTrue(Subscriber.objects.filter(email='demo@example.com').exists())


class SubscriptionFormTest(UnitTestBase):
    """Тест отображения формы подписки"""

    def setUp(self):
        super(SubscriptionFormTest, self).setUp()

        source_site = Site.objects.get(slugs='news')
        stamp = datetime.date.today()
        slug = self.random_string(10).lower()

        kwargs_ = {
            "year": stamp.year,
            "month": '%02d' % stamp.month,
            "day": '%02d' % stamp.day,
            "slug": slug,
        }
        self.form_url = reverse('news:news:read', kwargs=kwargs_)
        create_material('news', 'news', site=source_site, slug=slug, stamp=stamp, is_hidden=False)

    def test_form(self):
        """Форма для подписки на рассылку новостей"""

        user = self.create_user('test')
        G(Subscriber, email=user.email)

        response = self.app.get(self.form_url, user=user)
        self.assertNotContains(response, 'b-news-subscription-form')

        response = self.app.get(self.form_url, user=self.create_user('test2'))
        self.assertContains(response, 'b-news-subscription-form')

        response = self.app.get(self.form_url, user=self.create_anonymous_user())
        self.assertContains(response, 'b-news-subscription-form')
