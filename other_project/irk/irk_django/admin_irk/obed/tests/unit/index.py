# -*- coding: UTF-8 -*-

from __future__ import absolute_import

import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase

from irk.obed.models import Article, ArticleCategory, Establishment
from irk.options.models import Site
from irk.afisha.models import Event, Period, EventGuide, Sessions


class ObedIndexTestCase(UnitTestBase):
    """Главная страница обеда"""

    def _create_event(self, is_hidden, is_obed_announcement, start_date, end_date):
        event = G(Event, type=self.event_type, genre=self.genre, is_hidden=is_hidden,
                  is_obed_announcement=is_obed_announcement, parent=None)
        event_guide = G(EventGuide, event=event, guide=self.guide)
        period = G(Period, event_guide=event_guide, duration=None, start_date=start_date,
                   end_date=end_date)
        G(Sessions, period=period, time=datetime.time(12, 0))
        G(Sessions, period=period, time=datetime.time(13, 0))
        return event

    def setUp(self):
        super(ObedIndexTestCase, self).setUp()
        self.admin = self.create_user('admin', 'admin', is_admin=True)

    def test_articles(self):
        """Блок статей"""

        categories = [
            G(ArticleCategory, title=u'Критик', slug='critic'),
            G(ArticleCategory, title=u'Новости', slug='news'),
            G(ArticleCategory, title=u'Рецепты', slug='recipes'),
        ]

        site = Site.objects.get(slugs='obed')
        article_ct = ContentType.objects.get_for_model(Article)
        hidden = G(
            Article, section_category=categories[0], source_site=site, sites=[site, ], is_hidden=True,
            content_type=article_ct
        )
        G(
            Article, section_category=categories[0], source_site=site, sites=[site, ], is_hidden=False,
            content_type=article_ct, n=3
        )

        response = self.app.get(reverse('obed:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'obed/index.html')
        self.assertEqual(len(response.context['article_categories']), 3)
        articles = response.context['article_list']
        for article in articles:
            self.assertNotEqual(hidden.id, article.id)
        response = self.app.get(reverse('obed:index'), user=self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['article_categories']), 3)
        articles = response.context['article_list']
        self.assertIn(hidden, articles)

    def test_new_establishments(self):
        """Блок новых заведений"""

        G(Establishment, is_active=True, visible=True, is_new=False, n=3)
        G(Establishment, is_active=True, visible=True, is_new=True, n=2)
        G(Establishment, is_active=True, visible=False, is_new=True, n=1)

        response = self.app.get(reverse('obed:index'))

        self.assertEqual(len(response.context['new_establishments']), 2)
