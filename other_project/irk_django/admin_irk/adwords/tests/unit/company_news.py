# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import logging

from django.core.urlresolvers import reverse

from irk.tests.unit_base import UnitTestBase
from django_dynamic_fixture import G

from irk.adwords.models import CompanyNews, CompanyNewsPeriod
from irk.adwords.templatetags.adwords_tags import company_news

from irk.news.models import News

logger = logging.getLogger("tests")


class CompanyNewsTest(UnitTestBase):
    def test_news_pages(self):
        """Тестирование страниц новостей"""

        stamp = datetime.date.today()
        week_ago_stamp = datetime.date.today() - datetime.timedelta(7)

        for i in range(10):
            G(News, last_comment=None, is_hidden=False)

        news_1 = G(CompanyNews, stamp=stamp, last_comment=None, is_hidden=False)
        G(CompanyNewsPeriod, news=news_1, start=stamp, end=stamp)

        news_2 = G(CompanyNews, stamp=stamp, is_hidden=True, last_comment=None)
        G(CompanyNewsPeriod, news=news_2, start=stamp, end=stamp)

        news_3 = G(CompanyNews, stamp=week_ago_stamp, last_comment=None, is_hidden=False)
        G(CompanyNewsPeriod, news=news_3, start=stamp, end=stamp)

        page = self.app.get(reverse('company_news.read', kwargs={'news_id': news_2.pk}), status="*")
        self.assertEqual(404, page.status_code, "Hidden news for anonymous should return a 404")


    def test_news_templatetag(self):
        """Тестирование тэга вывода
           последних 2-х новостей
        """

        stamp = datetime.date.today()
        news = G(CompanyNews, stamp=stamp, last_comment=None, is_hidden=False)
        G(CompanyNewsPeriod, news=news, start=stamp, end=stamp)

        G(CompanyNews, stamp=stamp, is_hidden=True, last_comment=None, )
        G(CompanyNewsPeriod, news=news, start=stamp, end=stamp)

        result = company_news()
        news_list = result['news']
        self.assertEqual(1, len(news_list), "is_hidden news in template tag should be `hidden`")
