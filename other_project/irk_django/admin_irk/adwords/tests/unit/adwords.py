# -*- coding: UTF-8 -*-
import datetime
from irk.adwords.templatetags.adwords_tags import MultipleSiteAdWord
from irk.adwords.models import AdWord, AdWordPeriod
from irk.tests.unit_base import UnitTestBase
from django import template
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django_dynamic_fixture import G
from irk.options.models import Site


class AdWordsTest(UnitTestBase):
    """Рекламные новости"""

    def test_index(self):
        """Список рекламных новостей"""

        G(AdWord, n=35)
        response = self.app.get(reverse('adwords:index'))

        self.assertEqual(len(response.context['objects']), 20, 'Not all adWords were shown at first page')
        # ограничение выборки
        response = self.app.get(reverse('adwords:index') + '?limit=%d' % 10)
        self.assertEqual(len(response.context['objects']), 10, 'Limitation not work')
        # пагинация
        response = self.app.get(reverse('adwords:index') + '?page=%d' % 15)
        self.assertEqual(len(response.context['objects']), 15, 'Pagination not work')

    def test_read(self):
        """Просмотр рекламной новости"""

        adword = G(AdWord)
        response = self.app.get(reverse('adwords:read', args=(adword.pk, )))

        self.assertEqual(response.context['adword'], adword)


class AdWordsTemplateTagTest(UnitTestBase):
    """Шаблонный тег для вывода рекламных новостей"""

    def test_template_tag(self):
        """Блок рекламных новостей в разделе Новости"""

        stamp = datetime.date.today()
        news_site = Site.objects.get(slugs='news')
        first_title = 'The first adWords title'
        second_title = 'The second adWords title'

        # Создаем две новости, привязанных к Новостям
        ad_word1 = G(AdWord, title=first_title, sites=[news_site, ])
        G(AdWordPeriod, adword=ad_word1, start=stamp, end=stamp)

        ad_word2 = G(AdWord, title=second_title, sites=[news_site, ])
        G(AdWordPeriod, adword=ad_word2, start=stamp, end=stamp)

        request = RequestFactory().get(reverse('news:index'))
        request.csite = news_site
        node = MultipleSiteAdWord(limit=2, template='adwords/tags/inline_multiple_adwords.html', variable=None)
        context = template.Context({'request': request})
        response = node.render(context)

        # Вывелись обе новости
        self.assertIn(first_title, response)
        self.assertIn(second_title, response)
