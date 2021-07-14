# coding=utf-8
from __future__ import unicode_literals

import datetime

import pytest
from django.template import Template, Context
from pytest_django.asserts import assertTemplateUsed, assertTemplateNotUsed
from django_dynamic_fixture import G

from irk.adv.models import Place, Banner, Period


@pytest.mark.django_db
class TestIbanner:
    def test_should_not_throw_error(self):
        """ibanner работает в принципе"""

        context = Context()
        template = Template('{% load adv_tags %}{% ibanner ID=1 %}', name='str')

        # если не вылетает ошибка, значит работает
        with assertTemplateNotUsed('adv/div_none.html'):
            template.render(context)

    def test_should_render_banner(self):
        """рендерит баннер в заданном плейсе, если период вывода баннера позволяет"""
        place = G(Place, id=1)
        banner = G(Banner, iframe='', places=[place, ])
        today = datetime.date.today()
        G(Period, banner=banner, date_from=today, date_to=today)

        context = Context()
        template = Template('{% load adv_tags %}{% ibanner ID=1 %}', name='str')

        # рендерится
        with assertTemplateUsed('adv/div_none.html'):
            template.render(context)
