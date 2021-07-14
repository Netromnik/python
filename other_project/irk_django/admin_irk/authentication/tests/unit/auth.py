# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime

from django_dynamic_fixture import get
from django.core.urlresolvers import reverse

from irk.profiles.models import Profile, User

from irk.tests.unit_base import UnitTestBase


class RememberPasswordTestCase(UnitTestBase):
    """Тесты на восстановление пароля"""

    csrf_checks = False

    def test_set_password(self):
        """Изменение пароля"""

        hash_ = self.random_string(40)
        password = '123'

        profile = get(Profile, hash=hash_, hash_stamp=datetime.date.today())

        self.app.post('%s?hash=%s' % (reverse('profiles.views.auth.change'), hash_), params={
            'new_password1': password,
            'new_password2': password,
        })

        user = User.objects.get(profile=profile.pk)
        self.assertTrue(user.check_password(password))


class UsernameRegexTestCase(UnitTestBase):
    """Проверки на валидность юзернейма

    см. `auth.settings.USERNAME_REGEXP`"""

    def test(self):
        from irk.authentication.settings import USERNAME_REGEXP

        self.assertRegexpMatches(u'test', USERNAME_REGEXP)
        self.assertRegexpMatches(u'test TEST', USERNAME_REGEXP)
        self.assertRegexpMatches(u'Вася', USERNAME_REGEXP)
        self.assertRegexpMatches(u'wi-fi', USERNAME_REGEXP)
        self.assertRegexpMatches(u'wi_fi', USERNAME_REGEXP)
        self.assertRegexpMatches(u'wi fi', USERNAME_REGEXP)
        self.assertRegexpMatches(u'Петров Василий', USERNAME_REGEXP)
        self.assertRegexpMatches(u'Bob', USERNAME_REGEXP)
        self.assertRegexpMatches(u'АБВ абв 123 _ -', USERNAME_REGEXP)
        self.assertRegexpMatches(u'Петров В. В.', USERNAME_REGEXP)
        self.assertRegexpMatches(u'Вася.', USERNAME_REGEXP)
        self.assertRegexpMatches(u'-Bob-', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u' ', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'-', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'_', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'a  ', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'a--', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'Ли', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'Вася!', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'Вася&', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'Вася(', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'Вася)', USERNAME_REGEXP)
        self.assertNotRegexpMatches(u'Вася)', USERNAME_REGEXP)


class AuthorisationTestCase(UnitTestBase):
    """Тесты авторизации"""

    csrf_checks = False

    def test_login_logout(self):
        """Залогиниться/разлогиниться"""

        password = self.random_string(5)
        user = self.create_user('vasya', password)
        url = reverse('authentication:login')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

        response = self.app.post(url, params={'phone_email': user.email, 'password': password, },
                                 headers={'X_REQUESTED_WITH': 'XMLHttpRequest', })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '[1]')

        response = self.app.get(reverse('authentication:logout')).follow()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user.is_authenticated, False)

    def test_corporative_login_logout(self):
        """Залогиниться/разлогиниться корпоративным пользователем"""

        password = self.random_string(5)
        user = self.create_user('vasya', password, is_corporative=True)
        url = reverse('authentication:login')
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

        response = self.app.post(url, params={'phone_email': user.email, 'password': password, },
                                 headers={'X_REQUESTED_WITH': 'XMLHttpRequest', })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '[1]')

        response = self.app.get(reverse('authentication:logout')).follow()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user.is_authenticated, False)
