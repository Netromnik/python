# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django_dynamic_fixture import G

from irk.profiles.models import Profile
from irk.tests.unit_base import UnitTestBase
from irk.sms.models import PhoneNumber
from irk.utils.db.kv import get_redis


class UserTestCase(UnitTestBase):
    """Тестирование системы работы с данными пользователя"""

    csrf_checks = False

    def test_update_password(self):
        """Изменение пароля"""

        hash_ = self.random_string(40)

        user = self.create_user('user', password='111')
        profile = Profile.objects.get(user=user)
        profile.hash_stamp = datetime.datetime.now()
        profile.hash = hash_
        profile.save()

        url = reverse('authentication:profile:password')

        self.assertTrue(check_password('111', profile.user.password))

        # Форма для незалогиненых и без хэша недоступна
        response = self.app.get(url, status=404)
        self.assertEqual(response.status_code, 404)

        # Форма для незалогиненых и с неверным хэшом не доступна
        response = self.app.get('{0}?hash={1}'.format(url, self.random_string(40)), status=404)
        self.assertEqual(response.status_code, 404)

        # Форма для незалогиненых и с верным хэшом доступна
        response = self.app.get('{0}?hash={1}'.format(url, hash_))
        form = response.forms['form-update-response']
        form['password'] = '222'
        form.submit()
        profile = Profile.objects.get(user=user)
        self.assertTrue(check_password('222', profile.user.password))

        # Форма для залогиненых и без хэша недоступна
        response = self.app.get(url, user=user)
        form = response.forms['form-update-response']
        form['password'] = '333'
        form.submit()
        profile = Profile.objects.get(user=user)
        self.assertTrue(check_password('333', profile.user.password))

    def test_update(self):
        """Редактирование профиля"""

        user = self.create_user('user')
        url = reverse('authentication:profile:update')
        response = self.app.get(url, user=user)

        email = 'test@example.com'
        gender = 'f'
        birthday_day = 17
        birthday_month = 10
        birthday_year = 2000

        form = response.forms['auth-profile-edit']
        form['gender'] = gender
        form['email'] = email
        form['birthday_day'] = birthday_day
        form['birthday_month'] = birthday_month
        form['birthday_year'] = birthday_year
        form['subscribe'] = True
        form['comments_notify'] = True
        form.submit()

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.user.email, email)
        self.assertEqual(profile.gender, gender)
        self.assertEqual(profile.birthday, datetime.date(year=birthday_year, month=birthday_month, day=birthday_day))
        self.assertEqual(profile.subscribe, True)
        self.assertEqual(profile.comments_notify, True)

    def test_change_phone(self):
        """Привязать/изменить телефон профиля"""

        def mock_receive_code(phone_number):
            redis = get_redis()
            return redis.get('auth.join.phone_confirm.{0}'.format(phone_number))

        G(PhoneNumber, range_min=9500000000, range_max=9509999999)
        phone = '9501234567'
        user = self.create_user('user')
        url = reverse('authentication.views.profile.phone.link')

        response = self.app.get(url)
        self.assertEqual(response.status_code, 302)  # редирект на авторизацию

        response = self.app.get(url, user=user)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/users/phone/link.html')

        form = response.forms['phone-register']
        form['phone'] = phone
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/users/phone/confirm.html')

        form = response.forms['phone-confirm-form']
        form['code'] = mock_receive_code(phone)
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/users/update.html')
        self.assertEqual(response.context['user'].profile.phone, phone)

    def test_corporative_change_phone(self):
        """Корпоративные пользователи не могут менять телефон"""

        user = self.create_user('user', is_corporative=True)
        url = reverse('authentication.views.profile.phone.link')

        response = self.app.get(url, status='*', user=user)
        self.assertEqual(response.status_code, 403)

    def test_email_change(self):
        """Нельзя привязать емэйл, который уже используется"""

        user1 = self.create_user('user1')
        user1.email = 'a@example.org'
        user1.save()

        user2 = self.create_user('user2')
        user2.email = 'b@example.org'
        user2.save()

        # Пытаемся поменять email на email другого пользователя
        url = reverse('authentication:profile:update')
        response = self.app.get(url, user=user2)

        email = user1.email
        gender = 'f'
        birthday_day = 17
        birthday_month = 10
        birthday_year = 2000

        form = response.forms['auth-profile-edit']
        form['gender'] = gender
        form['email'] = email
        form['birthday_day'] = birthday_day
        form['birthday_month'] = birthday_month
        form['birthday_year'] = birthday_year
        form['subscribe'] = True
        form['comments_notify'] = True

        form.submit()

        self.assertNotEqual(user1.email, User.objects.get(id=user2.id).email)
