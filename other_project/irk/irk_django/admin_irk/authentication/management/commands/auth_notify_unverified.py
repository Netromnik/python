# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.template import Template, Context

from irk.profiles.models import Profile
from irk.utils.notifications import notify

template = u'''{% extends 'letter.html' %}

{% load site_utils str_utils news_tags %}

{% block content %}
    <p>Уважаемый пользователь, ваш логин на сайте IRK.ru заблокирован, поскольку вы не подтвердили его подлинность.</p>
    <p>Верифицировать аккаунт можно в настройках профиля. Инструкция находится по ссылке: <a href="http://www.irk.ru/verification/">http://www.irk.ru/verification/</a>.</p>
{% endblock %}
'''


class Command(BaseCommand):
    """Уведомление неверифицированных пользователей"""

    def handle(self, *args, **kwargs):
        tpl = Template(template)
        message = tpl.render(Context({}))

        for profile in Profile.objects.filter(is_verified=False, user__is_active=True):
            if not profile.user.email or 'example.org' in profile.user.email:
                continue

            notify(u'Ваш логин на сайте IRK.ru заблокирован', message, emails=(profile.user.email,))
